from typing import Optional, Annotated
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.core import auth_service as AuthService
from app.schemas.user_management import menu as MenuSchemas
from app.utils.responses import Response
from app.services.user_management import menu_service as MenuService
from app.core.permissions import check_permission


router = APIRouter()

# ---------------- Helper Function ----------------
def handle_exception(e: Exception, msg: str, code: int = 500):
    return MenuSchemas.MenuResponse(
        message=f"{msg}: {str(e)}",
        status_code=code,
        data=None
    )

# ---------------- Create Menu ----------------
@router.post(
    "/",
    response_model=MenuSchemas.MenuResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[check_permission(1, "/menus", "create")],
    response_model_exclude_none=True
)
def create_menu(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    menu: MenuSchemas.MenuCreate,
    db: Session = Depends(get_db)
):
    try:
        result = MenuService.create_menu(db, menu, login_id=current_user.id)
        return Response(
            json_data=result,
            message="Menu created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return handle_exception(e, "Menu creation failed", getattr(e, "status_code", 400))

# ---------------- List Menus ----------------
@router.get(
    "/",
    dependencies=[check_permission(1, "/menus", "view")],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
def list_menus(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: Optional[str] = None
):
    try:
        offset = (page - 1) * limit
        result = MenuService.get_menus(db, skip=offset, limit=limit, search=search)
        return Response(
            json_data=result,
            message="Menus fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching menus", getattr(e, "status_code", 500))


#---------------Module By ID-------------------------
@router.get(
    "/by-module/{module_id}",
    dependencies=[check_permission(1, "/menus", "view")],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
def list_menus_by_module(
    module_id: int,
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        result = MenuService.get_menus_by_module(
            db,
            module_id=module_id
        )
        return Response(
            json_data=result,
            message=f"Menus for module {module_id} fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching menus by module", getattr(e, "status_code", 500))



# ---------------- Get Menu by ID ----------------
@router.get(
    "/{menu_id}",
    response_model=MenuSchemas.MenuResponse,
    dependencies=[check_permission(1, "/menus", "view")],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
def get_menu_by_id(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    menu_id: int,
    db: Session = Depends(get_db)
):
    try:
        menu = MenuService.get_menu_by_id(db, menu_id)
        if not menu:
            return handle_exception(Exception("Menu not found"), "Fetching menu failed", 404)
        return Response(
            json_data=menu,
            message="Menu fetched successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error fetching menu", getattr(e, "status_code", 500))

# ---------------- Update Menu ----------------
@router.put(
    "/{menu_id}",
    response_model=MenuSchemas.MenuResponse,
    dependencies=[check_permission(1, "/menus", "edit")],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
def update_menu(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    menu_id: int,
    menu: MenuSchemas.MenuUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_menu = MenuService.update_menu(db, menu_id, menu, login_id=current_user.id)
        if not updated_menu:
            return handle_exception(Exception("Menu not found"), "Updating menu failed", 404)
        return Response(
            json_data=updated_menu,
            message="Menu updated successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error updating menu", getattr(e, "status_code", 500))

# ---------------- Delete Menu ----------------
@router.delete(
    "/{menu_id}",
    response_model=MenuSchemas.MenuResponse,
    dependencies=[check_permission(1, "/menus", "delete")],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
def delete_menu(
    current_user: Annotated[AuthService.User, Depends(AuthService.get_current_user)],
    menu_id: int,
    db: Session = Depends(get_db)
):
    try:
        deleted_menu = MenuService.delete_menu(db, menu_id, login_id=current_user.id)
        if not deleted_menu:
            return handle_exception(Exception("Menu not found"), "Deleting menu failed", 404)
        return Response(
            json_data=deleted_menu,
            message="Menu deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return handle_exception(e, "Error deleting menu", getattr(e, "status_code", 500))
