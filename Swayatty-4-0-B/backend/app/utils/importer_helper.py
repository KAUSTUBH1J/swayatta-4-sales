# app/helpers/importer.py

import csv
from io import StringIO
from fastapi import HTTPException
from sqlalchemy.orm import Session

def import_csv_to_model(file_content: bytes, db: Session, model):
    decoded = file_content.decode("utf-8-sig")  # utf-8-sig to handle BOM
    csv_reader = csv.DictReader(StringIO(decoded))

    model_columns = {column.name for column in model.__table__.columns}
    records_to_create = []

    for row in csv_reader:
        # Filter out unknown columns
        clean_row = {key: value for key, value in row.items() if key in model_columns}

        try:
            obj = model(**clean_row)
            records_to_create.append(obj)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing row: {row}. Error: {str(e)}")

    db.bulk_save_objects(records_to_create)
    db.commit()

    return len(records_to_create)
