from enum import Enum

class DiagnosisOption(str, Enum):
    Yes = True
    No  = False

class Types(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"