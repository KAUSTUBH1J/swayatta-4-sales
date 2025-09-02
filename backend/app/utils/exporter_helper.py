import csv
from io import StringIO
from typing import List, Optional, Callable, Dict, Any, Type

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import DeclarativeMeta


def export_model_with_relationships(
    db: Session,
    model: Type[DeclarativeMeta],
    search_fields: List[str],
    relationship_fields: Dict[str, Callable[[Any], Any]],
    search: Optional[str] = None,
    filename: str = "export.csv"
) -> StreamingResponse:
    
    # Build base query
    query = db.query(model).filter(model.is_deleted == False)

    # Apply search filters if needed
    if search:
        filters = []
        for field in search_fields:
            filters.append(getattr(model, field).ilike(f"%{search}%"))
        query = query.filter(or_(*filters))

    records = query.all()

    # Get base columns
    base_columns = [col.name for col in model.__table__.columns]
    extra_columns = list(relationship_fields.keys())
    all_columns = base_columns + extra_columns

    # Prepare data
    rows = []
    for record in records:
        row = {col: getattr(record, col) for col in base_columns}
        for key, func in relationship_fields.items():
            try:
                row[key] = func(record)
            except Exception:
                row[key] = ""
        rows.append(row)

    # Write to CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=all_columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
