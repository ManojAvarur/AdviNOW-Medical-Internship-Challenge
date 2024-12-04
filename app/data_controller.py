import datetime
from models import Business, Symptoms, Diagnostics
from typing import List, Dict, Tuple
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Select, Sequence, Row, Update
from utlis import Types

class ValueError(Exception):
    """Custom Exception"""
    ...

class DataController:
    # Holds DB Queried Data
    _business_db_data:     Tuple[str]       = None  # Holds Business Ids from DB
    _symptoms_db_data:     Tuple[str]       = None  # Holds Symptoms Ids from DB
    _diagnostics_db_data:  Dict[str, str]   = None  # Holds Combination of Business, Symptom & Diagnostics Ids from DB

    # Holds data which are to be processed in either INSERT / UPDATE state
    _business_data_to_proc:     Dict[Types, Dict[str, Business]]         
    _symptoms_data_to_proc:     Dict[Types, Dict[str, Symptoms]] 
    _diagnostics_data_to_proc:  Dict[Types, Dict[str, Diagnostics]] 

    def __init__(self, db: Session):
        """
        Sets DB instance and retrives all the Ids from DB

        Args:
            db: Database connected session 
        """
        if not db:
            raise ValueError("DB Connection not found!")
        
        # Storing DB session for future use
        self.db = db

        # Instantiating DB Store Values
        self._business_db_data      = {}
        self._symptoms_db_data      = {}
        self._diagnostics_db_data   = {}

        # Instantiating Data Process Values
        self._business_data_to_proc     = { Types.INSERT: {}, Types.UPDATE: {} }
        self._symptoms_data_to_proc     = { Types.INSERT: {}, Types.UPDATE: {} }
        self._diagnostics_data_to_proc  = { Types.INSERT: {}, Types.UPDATE: {} }

        # Fetching currently exsiting data from DB
        self._business_db_data       = tuple(row[0] for row in db.execute(Select(Business.id).order_by(Business.id)))
        self._symptoms_db_data       = tuple(row[0] for row in db.execute(Select(Symptoms.id).order_by(Symptoms.id)))

        diagnostics_data = db.execute(Select(Diagnostics.id, Diagnostics.business_id, Diagnostics.symptom_id, Diagnostics.Diagnostics))
        for row in diagnostics_data:
            self._diagnostics_db_data[self.create_diagnostics_hash(row)] = row.id

        print(self._diagnostics_db_data.keys())
        print(self._diagnostics_db_data.values())

        # print("business_db_data", self._business_db_data)
        # print("_symptoms_db_data", self._symptoms_db_data)
        # print("_diagnostics_db_data", self._diagnostics_db_data)

    def add_data(self, value: Business | Symptoms | Diagnostics) -> None:
        """
        Appends value to list based on the type of data
        """
        if isinstance(value, Diagnostics):
            self.diagnostics_data_processor(value)
            return

        self.business_or_symptoms_data_processor(value)

    def check_id_exists_in_db(self, id: str, db_data: Tuple[str]) -> bool:
        """
        Checks if the id is already in databse

        Args:
            id:      Id which has to be compared 
            db_data: Value to which the Id has to be compared against

        Returns:
            bool: Returns True, if the value is already in DB
        """
        # print(f"\n\n{type(id)} {id} in {db_data}: {id in db_data}\n\n")
        return id in db_data
    
    def check_id_exists_in_cur_ins(self, 
                                value: Business | Symptoms, 
                                cur_proc_data: Dict[Types, Dict[str, Business]] | 
                                                Dict[Types, Dict[str, Symptoms]] | 
                                                Dict[Types, Dict[str, Diagnostics]]
    ) -> bool:
        """
        Checks if the id is already under INSERT state processing

        Args:
            value:          Value of which the Id has to be compared 
            cur_proc_data:  Value to which the Id has to be compared against

        Returns:
            bool: Returns True, if the value is already in processing state
        """
        return value.id in cur_proc_data[Types.INSERT]

    def business_or_symptoms_data_processor(self, value: Business | Symptoms) -> None:
        """
        Check instance of value for either Business / Symptoms
            1. If the data already exists in DB, it will be set to update state
            2. If the data is in insert state, set this also to update state

        Args:
            value: Value to be processed
        """

        data_to_proc = None
        db_data = None

        if isinstance(value, Business):
            data_to_proc = self._business_data_to_proc
            db_data = self._business_db_data
        else:
            data_to_proc = self._symptoms_data_to_proc
            db_data = self._symptoms_db_data

        if self.check_id_exists_in_db(value.id, db_data) or self.check_id_exists_in_cur_ins(value, data_to_proc):
            data_to_proc[Types.UPDATE][value.id] = value
            return
        
        data_to_proc[Types.INSERT][value.id] = value

    def diagnostics_data_processor(self, value: Diagnostics) -> None:
        """
        1. If the data already exists in DB, it will be set to update state
        2. If the data is in insert state, set this also to update state

        Args:
            value: Value to be processed
        """
        diagnostic_hash = self.create_diagnostics_hash(value)

        if self.check_id_exists_in_db(diagnostic_hash, self._diagnostics_db_data) or \
            self.check_id_exists_in_cur_ins(value, self._diagnostics_data_to_proc):
            self._diagnostics_data_to_proc[Types.UPDATE][diagnostic_hash] = value
            return
        
        self._diagnostics_data_to_proc[Types.INSERT][diagnostic_hash] = value
        
    def create_diagnostics_hash(self, diagnostic: Diagnostics) -> str:
        """
        Generates a unique hash from Diagnostics data

        Args:
            diagnostic: Diagnostics data

        Returns:
            str: Combination of bussiness, symptom and diagnostic data
        """
        return f"{diagnostic.business_id}-{diagnostic.symptom_id}-{diagnostic.Diagnostics}"

    def upsert_business_data(self) -> None:
        """
        Inserts and Updates business data which are under processing
        """

        if len(self._business_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._business_data_to_proc[Types.INSERT].values())
            self.db.commit()

        mappings = []
        for row in self._business_data_to_proc[Types.UPDATE].values():
            row.updated_at = datetime.datetime.now()
            mappings.append(row.to_dict())
        
        if len(mappings) > 0:
            self.db.bulk_update_mappings(Business, mappings)
            self.db.commit()

    def upsert_symptoms_data(self):
        """
        Inserts and Updates symptoms data which are under processing
        """
        if len(self._symptoms_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._symptoms_data_to_proc[Types.INSERT].values())
            self.db.commit()

        mappings = []
        for row in self._symptoms_data_to_proc[Types.UPDATE].values():
            row.updated_at = datetime.datetime.now()
            mappings.append(row.to_dict())
        
        if len(mappings) > 0:
            self.db.bulk_update_mappings(Symptoms, mappings)
            self.db.commit()


    def upsert_diagnostics_data(self):
        """
        Inserts and Updates diagnostics data which are under processing
        """
        if len(self._diagnostics_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._diagnostics_data_to_proc[Types.INSERT].values())
            self.db.commit()

        mappings = []
        for row in self._diagnostics_data_to_proc[Types.UPDATE].values():
            row.updated_at = datetime.datetime.now()
            row.id = self._diagnostics_db_data[self.create_diagnostics_hash(row)]
            mappings.append(row.to_dict())
        
        if len(mappings) > 0:
            self.db.bulk_update_mappings(Diagnostics, mappings)
            self.db.commit()