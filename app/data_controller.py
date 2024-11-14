import datetime
from models import Business, Symptoms, Diagnostics
from typing import List, Dict, Tuple
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Select, Sequence, Row, Update

class Types(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"

class ValueError(Exception):
    """Custom Exception"""
    ...

# class DataController:
#     # Holds DB Queried Data
#     _business_db_data:     Sequence[Row[Business]]     = None
#     _symptoms_db_data:     Sequence[Row[Symptoms]]     = None
#     _diagnostics_db_data:  List[str]                   = None

#     _business_data_to_proc: Dict[Types, Dict[str, Business]]         = { Types.INSERT: {}, Types.UPDATE: {} }

#     _symptoms_data_to_proc: Dict[Types, Dict[str, Symptoms]]         = { Types.INSERT: {}, Types.UPDATE: {} }

#     _diagnostics_data_to_proc: Dict[Types, Dict[str, Diagnostics]]   = { Types.INSERT: {}, Types.UPDATE: {} }

#     def __init__(self, db: Session):
#         if not db:
#             raise ValueError("DB Connection not found!")
        
#         self._business_db_data       = db.execute(Select(Business.id).order_by(Business.id)).all()
#         self._symptoms_db_data       = db.execute(Select(Symptoms.id).order_by(Symptoms.id)).all()
#         diagnostics_db_data          = db.execute(Select(Diagnostics.id, Diagnostics.business_id, Diagnostics.symptom_id))

#         self._diagnostics_db_data = []
#         for row in diagnostics_db_data:
#             self._diagnostics_db_data.append(self.create_diagnostics_hash(row))

#     def add_data(self, value: Business | Symptoms | Diagnostics) -> None:
#         """
#             1. If the data already exists in DB, it will be set to update state
#             2. If the data is in insert state, set this also to update state
#         """
#         if isinstance(value, Diagnostics):
#             self.diagnostics_data_processor(value)
#             return

#         self.business_or_symptoms_data_processor(value)


#     def check_id_exists_in_db(self, 
#                             id: str, 
#                             db_data: Sequence[Row[Business]] | 
#                                         Sequence[Row[Symptoms]] | 
#                                         List[str]
#     ) -> bool:
#         return id in db_data
    

#     def check_id_exists_in_cur_ins(self, 
#                                 value: Business | Symptoms, 
#                                 cur_proc_data: Dict[Types, Dict[str, Business]] | 
#                                                 Dict[Types, Dict[str, Symptoms]] | 
#                                                 Dict[Types, Dict[str, Diagnostics]]
#     ) -> bool:
#         return value.id in cur_proc_data[Types.INSERT]

#     def business_or_symptoms_data_processor(self, value: Business | Symptoms):
#         data_to_proc = None
#         db_data = None

#         if isinstance(value, Business):
#             data_to_proc = self._business_data_to_proc
#             db_data = self._business_db_data
#         else:
#             data_to_proc = self._symptoms_data_to_proc
#             db_data = self._symptoms_db_data

#         if self.check_id_exists_in_db(value.id, db_data) or self.check_id_exists_in_cur_ins(value, data_to_proc):
#             data_to_proc[Types.UPDATE][value.id] = value
#             return
        
#         data_to_proc[Types.INSERT][value.id] = value

#     def diagnostics_data_processor(self, value):
#         diagnostic_hash = self.create_diagnostics_hash(value)

#         if self.check_id_exists_in_db(diagnostic_hash, self._diagnostics_db_data) or \
#             self.check_id_exists_in_cur_ins(value, self._diagnostics_data_to_proc):
#             self._diagnostics_data_to_proc[Types.UPDATE][value.id] = value
#             return
        
#         self._diagnostics_data_to_proc[Types.INSERT][diagnostic_hash] = value
        
#     def create_diagnostics_hash(self, diagnostic: Diagnostics) -> str:
#         return f"{diagnostic.business_id}-{diagnostic.symptom_id}-{diagnostic.Diagnostics}"

#     def upsert_business_data(self):
#         print("\n\n-------------------------------------")

#         print("--------Business For Insert----------")
#         for i, (k, v) in enumerate(self._business_data_to_proc[Types.INSERT].items()):
#             print(i, k, v)

#         print("--------Business For Update----------")
#         for i, (k, v) in enumerate(self._business_data_to_proc[Types.UPDATE].items()):
#             print(i, k, v)

#         print("\n\n-------------------------------------")


#     def upsert_symptoms_data(self):
#         print("\n\n-------------------------------------")
#         print("\n\n--------Symptoms For Insert----------")

#         for i, (k, v) in enumerate(self._symptoms_data_to_proc[Types.INSERT].items()):
#             print(i, k, v)

#         print("--------Symptoms For Update----------")
#         for i, (k, v) in enumerate(self._symptoms_data_to_proc[Types.UPDATE].items()):
#             print(i, k, v)

#         print("\n\n-------------------------------------")


#     def upsert_diagnostics_data(self):
#         print("\n\n-------------------------------------")

#         print("\n\n--------Diagnostics For Insert----------")
#         for i, (k, v) in enumerate(self._diagnostics_data_to_proc[Types.INSERT].items()):
#             print(i, k, v)

#         print("--------diagnostics For Update----------")
#         for i, (k, v) in enumerate(self._diagnostics_data_to_proc[Types.UPDATE].items()):
#             print(i, k, v)

#         print("\n\n-------------------------------------")
        




class DataController:
    # Holds DB Queried Data
    _business_db_data:     Tuple[str]   = None  # Holds Business Ids from DB
    _symptoms_db_data:     Tuple[str]   = None  # Holds Symptoms Ids from DB
    _diagnostics_db_data:  Tuple[str]   = None  # Holds Combination of Business, Symptom,   Ids from DB

    _business_data_to_proc: Dict[Types, Dict[str, Business]]         = { Types.INSERT: {}, Types.UPDATE: {} }
    _symptoms_data_to_proc: Dict[Types, Dict[str, Symptoms]]         = { Types.INSERT: {}, Types.UPDATE: {} }
    _diagnostics_data_to_proc: Dict[Types, Dict[str, Diagnostics]]   = { Types.INSERT: {}, Types.UPDATE: {} }

    def __init__(self, db: Session):
        if not db:
            raise ValueError("DB Connection not found!")
        
        self.db = db
        self._business_db_data       = tuple(row[0] for row in db.execute(Select(Business.id).order_by(Business.id)))
        self._symptoms_db_data       = tuple(row[0] for row in db.execute(Select(Symptoms.id).order_by(Symptoms.id)))
        self._diagnostics_db_data    = tuple(self.create_diagnostics_hash(row[0]) for row in db.execute(Select(Diagnostics.id, Diagnostics.business_id, Diagnostics.symptom_id, Diagnostics.Diagnostics)))

    def add_data(self, value: Business | Symptoms | Diagnostics) -> None:
        """
            1. If the data already exists in DB, it will be set to update state
            2. If the data is in insert state, set this also to update state
        """
        if isinstance(value, Diagnostics):
            self.diagnostics_data_processor(value)
            return

        self.business_or_symptoms_data_processor(value)

    def check_id_exists_in_db(self, id: str, db_data: Tuple[str]) -> bool:
        return id in db_data
    
    def check_id_exists_in_cur_ins(self, 
                                value: Business | Symptoms, 
                                cur_proc_data: Dict[Types, Dict[str, Business]] | 
                                                Dict[Types, Dict[str, Symptoms]] | 
                                                Dict[Types, Dict[str, Diagnostics]]
    ) -> bool:
        return value.id in cur_proc_data[Types.INSERT]

    def business_or_symptoms_data_processor(self, value: Business | Symptoms):
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

    def diagnostics_data_processor(self, value):
        diagnostic_hash = self.create_diagnostics_hash(value)

        if self.check_id_exists_in_db(diagnostic_hash, self._diagnostics_db_data) or \
            self.check_id_exists_in_cur_ins(value, self._diagnostics_data_to_proc):
            self._diagnostics_data_to_proc[Types.UPDATE][value.id] = value
            return
        
        self._diagnostics_data_to_proc[Types.INSERT][diagnostic_hash] = value
        
    def create_diagnostics_hash(self, diagnostic: Diagnostics) -> str:
        return f"{diagnostic.business_id}-{diagnostic.symptom_id}-{diagnostic.Diagnostics}"

    def upsert_business_data(self):
        if len(self._business_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._business_data_to_proc[Types.INSERT].values())
            self.db.commit()

        for row in self._business_data_to_proc[Types.UPDATE].values():
            value = {}

            if row.name:
                value['name'] = row.name

            
            print(Update(Business).where(Business.id == row.id).values(row))

    def upsert_symptoms_data(self):
        if len(self._symptoms_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._symptoms_data_to_proc[Types.INSERT].values())
            self.db.commit()

        # exit(0)
        
        # for row in self._symptoms_data_to_proc[Types.UPDATE].values():
        #     stmt = (
        #         Update(Symptoms)
        #         .where(Symptoms.id == row.id) 
        #         .values(name=row.name, updated_at=datetime.datetime.now()) 
        #     )

        #     self.db.execute(stmt) 

        # self.db.commit()


    def upsert_diagnostics_data(self):
        if len(self._diagnostics_data_to_proc[Types.INSERT].values()) > 0:
            self.db.bulk_save_objects(self._diagnostics_data_to_proc[Types.INSERT].values())
            self.db.commit()