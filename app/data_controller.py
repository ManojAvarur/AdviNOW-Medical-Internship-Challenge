from models import Business, Symptoms, Diagnostics
from typing import List, Dict, Annotated
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Select, Sequence, Row

class Types(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"

class ValueError(Exception):
    """Custom Exception"""
    ...

class DataController:
    # Holds DB Queried Data
    _business_db_data:     Sequence[Row[Business]]     = None
    _symptoms_db_data:     Sequence[Row[Symptoms]]     = None
    _diagnostics_db_data:  Sequence[Row[Diagnostics]]  = None

    _business_data_to_proc: Dict[Types, Dict[str, Business]]         = { Types.INSERT: {}, Types.UPDATE: {} }

    _symptoms_data_to_proc: Dict[Types, Dict[str, Symptoms]]         = { Types.INSERT: {}, Types.UPDATE: {} }

    _diagnostics_data_to_proc: Dict[Types, Dict[str, Diagnostics]]   = { Types.INSERT: {}, Types.UPDATE: {} }

    def __init__(self, db: Session):
        self._business_db_data       = db.execute(Select(Business.id).order_by(Business.id)).all()
        self._symptoms_db_data       = db.execute(Select(Symptoms.id).order_by(Symptoms.id)).all()
        self._diagnostics_db_data    = db.execute(Select(Diagnostics.id, Diagnostics.business_id, Diagnostics.symptom_id)).all()

    def add_data(self, value: Business | Symptoms | Diagnostics) -> None:
        """
            TODO:
            1. If the data already exists in DB, set it to update state
            2. If the data is in insert state, set this also to update state
        """
        if isinstance(value, Diagnostics):
            self.diagnostics_data_proc(value)
            return

        self.business_or_symptons_data_processor(value)


    def check_id_exists_in_db(self, 
                            id: str, 
                            db_data: Sequence[Row[Business]] | 
                                        Sequence[Row[Symptoms]] | 
                                        Sequence[Row[Diagnostics]]
    ) -> bool:
        return id in db_data
    

    def check_id_exists_in_cur_ins(self, 
                                value: Business | Symptoms, 
                                cur_proc_data: Dict[Types, Dict[str, Business]] | Dict[Types, Dict[str, Business]]
    ) -> bool:
        return value.id in cur_proc_data[Types.INSERT]

    def business_or_symptons_data_processor(self, value: Business | Symptoms):
        data_to_proc = None
        db_data = None

        if isinstance(value, Business):
            data_to_proc = self._business_data_to_proc
            db_data = self._business_db_data
        else:
            data_to_proc = self._symptoms_data_to_proc
            db_data = self._symptoms_db_data

        if self.check_id_exists_in_db(value.id, db_data) or self.check_id_exists_in_cur_ins(value, data_to_proc):
            self.data_to_proc[Types.UPDATE][value.id] = value
            return
        
        self.data_to_proc[Types.INSERT] = value

    def diagnostics_data_processor(self):
        ...
