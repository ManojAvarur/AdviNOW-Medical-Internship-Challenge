from fastapi import APIRouter, Response, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated, Literal, Optional
from models import Business, Symptoms, Diagnostics
from pandas import read_csv
from database import db_instance
from sqlalchemy.orm import Session
from sqlalchemy import Select, bindparam, insert
from utlis import business_data_ctrl, symptoms_data_ctrl
from sqlalchemy.dialects import postgresql
from data_controller import DataController, ValueError

router = APIRouter()

@router.get('/')
def redirect_to_docs():
    return RedirectResponse("/docs")

@router.get('/status')
async def get_status(res: Response):
    try:
        return { "status": "Health OK" }
    except Exception as e:
        res.status_code = 500
        return { "error": str(e) }

@router.post('/csv-to-db')
def csv_to_database(
    file: Optional[Annotated[UploadFile, File(...,media_type="text/csv")]],
    db: Session = Depends(db_instance)
):
    # try:
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

        return data_controller
    # except Exception as e:
    #     return JSONResponse(
    #         content = { "error": f"Error:  {str(e)}" },
    #         status_code = 400
    #     )