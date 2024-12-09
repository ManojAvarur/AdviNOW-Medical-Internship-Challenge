from enum import Enum

class DiagnosisOption(str, Enum):
    Yes = "Yes"
    No  = "No"

class Types(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"