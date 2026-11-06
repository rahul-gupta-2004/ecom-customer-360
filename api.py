from fastapi import FastAPI, HTTPException, UploadFile, File
import pandas as pd
import tempfile
import os
from src.ingest import load_raw_data, validate_data
from src.transform import apply_transformations
from src.load import load_data_to_postgres

app = FastAPI(title="Customer 360 Data Pipeline API", version="1.0")

@app.post("/api/v1/ingest")
async def ingest_customer_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        raw_df = load_raw_data(tmp_path)
        validated_df = validate_data(raw_df)
        transformed_df = apply_transformations(validated_df)
        load_data_to_postgres(transformed_df, table_name="customer_360_pipeline_data")
        
        return {
            "status": "success",
            "filename": file.filename,
            "rows_processed": len(transformed_df)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)