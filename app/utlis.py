from models import Business, Symptoms
from sqlalchemy import Row, Sequence

def business_data_ctrl( business_id: str, 
                        business_name: str, 
                        data_controller: dict, 
                        queried_business_data: Sequence[Row]
) -> None:
    
    business_id = business_id.strip()
    business_name = business_name.strip()

    if not business_id or not business_name:
        return
    
    if business_id in queried_business_data:
        data_controller["data_to_update"]["business_data"].append(
            Business(id=business_id, name=business_name, updated_at=None)
        )

        return

    data_controller["data_to_insert"]["business_data"].append(
        Business(id=business_id, name=business_name)
    )

def symptoms_data_ctrl( symptom_id: str, 
                        symptom_name: str, 
                        data_controller: dict, 
                        queried_symptom_data: Sequence[Row]
) -> None:
    
    symptom_id = symptom_id.strip()
    symptom_name = symptom_name.strip()

    if not symptom_id or not symptom_name:
        return
    
    if symptom_id in queried_symptom_data:
        data_controller["data_to_update"]["symptoms_data"].append(
            Symptoms(id=symptom_id, name=symptom_name, updated_at=None)
        )
        
        return

    data_controller["data_to_insert"]["symptoms_data"].append(
        Symptoms(id=symptom_id, name=symptom_name)
    )

# def diagnostics_data_ctrl():
    