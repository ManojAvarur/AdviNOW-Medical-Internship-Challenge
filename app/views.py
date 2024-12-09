from fastapi import APIRouter, Response, UploadFile, File, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated, Literal, Optional, Union
from models import Business, Symptoms, Diagnostics
from pandas import read_csv
from database import db_instance
from sqlalchemy.orm import Session
from sqlalchemy import Select
from utlis import DiagnosisOption
from data_controller import DataController, ValueError

router = APIRouter()

@router.get('/', include_in_schema=False)
def redirect_to_docs():
    """
    Redirects request /docs
    """
    return RedirectResponse("/docs")

@router.get('/status', name="System status")
def get_status(res: Response, db: Session = Depends(db_instance)):
    """
    Returns the health / status of the system
    """
    try:
        db.execute(Select(Business.id).limit(1))
        return { "status": "Health OK" }
    except Exception as e:
        res.status_code = 500
        return { "error": str(e) }

@router.post('/csv-to-db', name="CSV to database parser")
def csv_to_database(
    file: Optional[Annotated[UploadFile, File(...,media_type="text/csv")]],
    db: Session = Depends(db_instance)
):
    """
    Parses the provided CSV file and uploades the data into database
    """
    try:
        if not file or file.headers["content-type"] != "text/csv":
            return JSONResponse(
                content = { "error": "Please select a .csv file!" },
                status_code = 400
            )
        
        data = read_csv(file.file).to_dict(orient="index")

        data_controller = DataController(db)

        for i in data:
            # User Uploaded Data
            business_id :str         = str(data[i]["Business ID"])
            business_name :str       = data[i]["Business Name"]
            symptom_code :str        = str(data[i]["Symptom Code"])
            symptom_name :str        = data[i]["Symptom Name"]

            symptom_diagnostic_str :str  = data[i]["Symptom Diagnostic"]
            symptom_diagnostic :bool     = symptom_diagnostic_str.lower() in ["yes", "true", "y", "1"]

            data_controller.add_data(Business(id=business_id, name=business_name))
            data_controller.add_data(Symptoms(id=symptom_code, name=symptom_name))
            data_controller.add_data(Diagnostics(business_id=business_id, symptom_id=symptom_code, Diagnostics=symptom_diagnostic))

        data_controller.upsert_business_data()
        data_controller.upsert_symptoms_data()
        data_controller.upsert_diagnostics_data()

        return JSONResponse(
            content={
                "message": "CSV Parsed Successfully!"
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content = { "error": f"Error:  {str(e)}" },
            status_code = 400
        )
    
@router.get('/fetch-data', name="Fetch data from database")
def fetch_data(business_id: Optional[str] = None, diagnosis: DiagnosisOption = Query(default=None), db: Session = Depends(db_instance)):
    """
    Fetches data from the database based on the provided parameters:
    1. If only a business ID is given, all diagnoses for that business ID are returned.
    2. If no diagnosis filter is provided, all diagnoses are returned; otherwise, the data is filtered based on the provided criteria.
    """

    to_query = Select(
        Business.id.label("business_id"),
        Business.name.label("business_name"),
        Symptoms.id.label("symptom_id"),
        Symptoms.name.label("symptom_name"),
        Diagnostics.Diagnostics.label("diagnosis")
    ).join(
        Business, Diagnostics.business_id == Business.id
    ).join(
        Symptoms, Diagnostics.symptom_id == Symptoms.id
    )

    if business_id != None and len(business_id.strip()) > 0:
        to_query = to_query.where(Business.id == business_id.strip())

    if diagnosis != None:
        to_query = to_query.where(Diagnostics.Diagnostics == (diagnosis == DiagnosisOption.Yes))

    queried_data = db.execute(to_query)

    parsed_data = [
        {
            "business_id"   : row.business_id,
            "business_name" : row.business_name,
            "symptom_id"    : row.symptom_id,
            "symptom_name"  : row.symptom_name,
            "diagnosis"     : row.diagnosis
        }
        for row in queried_data
    ]

    return JSONResponse(content=parsed_data)


