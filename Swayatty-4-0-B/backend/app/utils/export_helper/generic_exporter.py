import csv
from fastapi.responses import StreamingResponse
from io import StringIO
from typing import List, Type
from pydantic import BaseModel

def export_to_csv(data: List[BaseModel], schema: Type[BaseModel], filename="export.csv"):
    output = StringIO()
    writer = csv.writer(output)

    # Extract headers from schema
    headers = list(schema.model_fields.keys())
    writer.writerow(headers)

    for item in data:
        row = [getattr(item, field, "") for field in headers]
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
