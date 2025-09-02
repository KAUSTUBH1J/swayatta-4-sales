from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Annotated
from typing import Any, Dict, Set
from app.utils.env import env_get
from app.models.user_management.user import User
from app.models.user_management.menu import Menu
from app.models.user_management.permission import Permission
from app.models.user_management.role_permission import RolePermission
from app.models.user_management.user_permission import UserPermission
from app.services.user_management import user_service as UserService
from app.database.db import get_db



# Config and setup
SECRET_KEY = env_get("SECRET_KEY")
ALGORITHM = env_get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(env_get("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/swag-token")


# Password hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Authenticate user
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.is_deleted or not user.is_active:
        return None
    return user


# Decode and verify token
def verify_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# Dependency to get current user from token
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: Optional[str] = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user




# Dependency to get current user info with role permission for token verify



async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns current user's info, assigned modules, menus, and permissions.
    Permissions = RolePermissions + UserPermissions (union)
    """

    # --- Step 0: Parse assigned modules ---
    assigned_modules = [
        int(m.strip()) for m in (current_user.assign_modules or "").split(",") if m.strip()
    ]

    if not assigned_modules:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role_id": current_user.role_id,
            "assigned_modules": [],
            "menus": []
        }

    # --- Step 1: Fetch all menus for assigned modules ---
    menus = db.query(Menu).filter(
        Menu.module_id.in_(assigned_modules),
        Menu.is_deleted == False,
        Menu.is_active == True
    ).all()

    # --- Step 2: Build permissions map {id: set(permission_ids)} ---
    menu_permissions_map: Dict[int, Set[int]] = {}

    # 2A: Role-based permissions
    if current_user.role_id:
        role_perms = db.query(RolePermission).filter(
            RolePermission.role_id == current_user.role_id,
            RolePermission.module_id.in_(assigned_modules),
            RolePermission.is_deleted == False,
            RolePermission.is_active == True
        ).all()

        for rp in role_perms:
            perm_ids = [
                int(pid.strip()) for pid in (rp.permission_ids or "").split(",") if pid.strip().isdigit()
            ]
            menu_permissions_map.setdefault(rp.id, set()).update(perm_ids)

    # 2B: User-specific permissions
    user_perms = db.query(UserPermission).filter(
        UserPermission.user_id == current_user.id,
        UserPermission.module_id.in_(assigned_modules),
        UserPermission.is_deleted == False,
        UserPermission.is_active == True
    ).all()

    for up in user_perms:
        perm_ids = [
            int(pid.strip()) for pid in (up.permission_ids or "").split(",") if pid.strip().isdigit()
        ]
        menu_permissions_map.setdefault(up.id, set()).update(perm_ids)

    # --- Step 3: Fetch Permission names ---
    all_permission_ids = {pid for perms in menu_permissions_map.values() for pid in perms}
    permission_dict = {
        p.id: p.name
        for p in db.query(Permission)
        .filter(Permission.id.in_(all_permission_ids), Permission.is_deleted == False)
        .all()
    }

    # --- Step 4: Build hierarchical menu tree ---
    def build_menu(menu: Menu):
        perm_ids = menu_permissions_map.get(menu.id, set())
        perm_names = [permission_dict[pid] for pid in perm_ids if pid in permission_dict]

        children = [build_menu(child) for child in menus if child.parent_id == menu.id]
        children = [c for c in children if c]

        if not perm_names and not children:
            return None

        return {
            "id": menu.id,
            "module_id": menu.module_id,
            "name": menu.name,
            "path": menu.path,
            "is_sidebar": menu.is_sidebar,
            "icon":menu.icon,
            "order_index": menu.order_index,  
            "permissions": perm_names,
            "children": children
        }

    final_menus = [m for m in (build_menu(menu) for menu in menus if menu.parent_id is None) if m]

    # --- Step 5: Return structured response ---
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "assigned_modules": assigned_modules,
        "menus": final_menus
    }




async def get_current_user_info_old(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns current user's info, assigned modules, menus, and permissions.
    Permissions = RolePermissions + UserPermissions (union)
    """

    # --- Step 0: Parse assigned modules ---
    assigned_modules = [
        int(m.strip()) for m in (current_user.assign_modules or "").split(",") if m.strip()
    ]

    if not assigned_modules:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role_id": current_user.role_id,
            "assigned_modules": [],
            "menus": []
        }

    # --- Step 1: Fetch all menus for assigned modules ---
    menus = db.query(Menu).filter(
        Menu.module_id.in_(assigned_modules),
        Menu.is_deleted == False,
        Menu.is_active == True
    ).all()

    # --- Step 2: Build permissions map {id: set(permission_ids)} ---
    menu_permissions_map: Dict[int, Set[int]] = {}

    # 2A: Role-based permissions (base)
    if current_user.role_id:
        role_perms = db.query(RolePermission).filter(
            RolePermission.role_id == current_user.role_id,
            RolePermission.module_id.in_(assigned_modules),
            RolePermission.is_deleted == False,
            RolePermission.is_active == True
        ).all()

        for rp in role_perms:
            perm_ids = [
                int(pid.strip()) for pid in (rp.permission_ids or "").split(",") if pid.strip()
            ]
            menu_permissions_map.setdefault(rp.id, set()).update(perm_ids)

    # 2B: User-specific permissions (additional)
    user_perms = db.query(UserPermission).filter(
        UserPermission.user_id == current_user.id,
        UserPermission.module_id.in_(assigned_modules),
        UserPermission.is_deleted == False,
        UserPermission.is_active == True
    ).all()

    for up in user_perms:
        menu_permissions_map.setdefault(up.id, set()).add(up.permission_id)

    # --- Step 3: Fetch Permission names ---
    all_permission_ids = {pid for perms in menu_permissions_map.values() for pid in perms}
    permission_dict = {
        p.id: p.name
        for p in db.query(Permission)
        .filter(Permission.id.in_(all_permission_ids), Permission.is_deleted == False)
        .all()
    }

    # --- Step 4: Build hierarchical menu tree ---
    def build_menu(menu: Menu):
        perm_ids = menu_permissions_map.get(menu.id, set())
        perm_names = [permission_dict[pid] for pid in perm_ids if pid in permission_dict]

        children = [build_menu(child) for child in menus if child.parent_id == menu.id]
        children = [c for c in children if c]

        if not perm_names and not children:
            return None

        return {
            "id": menu.id,
            "module_id": menu.module_id,
            "name": menu.name,
            "path": menu.path,
            "is_sidebar": menu.is_sidebar,
            "permissions": perm_names,
            "children": children
        }

    final_menus = [m for m in (build_menu(menu) for menu in menus if menu.parent_id is None) if m]

    # --- Step 5: Return structured response ---
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "assigned_modules": assigned_modules,
        "menus": final_menus
    }


