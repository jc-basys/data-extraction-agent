# Saves JSON data to SQL tables (other than provider, department, and visit tables)  

from datetime import datetime
from sqlalchemy.orm import Session
from schemas.sql_schema import (
    Provider, Department, Visit, VisitNotes, Diagnosis, Symptom,
    Medication, VitalSigns, LabResult, ImagingStudy, ProcedureTreatment
)

from sqlalchemy.inspection import inspect

class SQLSaver:
    def insert_non_patient_entities(self, session: Session, data: dict) -> None:
        """
        Inserts all non-patient entities into the database.
        Only includes fields that are not None and are defined in the model.
        """
        model_map = {
            "visitnotes": VisitNotes,
            "diagnosis": Diagnosis,
            "symptom": Symptom,
            "medication": Medication,
            "vitalsigns": VitalSigns,
            "labresult": LabResult,
            "imagingstudy": ImagingStudy,
            "proceduretreatment": ProcedureTreatment,
            "provider": Provider,
            "department": Department
        }

        for key, model in model_map.items():
            records = data.get(key)
            if not records:
                continue

            if isinstance(records, dict):
                records = [records]

            valid_columns = {col.key for col in inspect(model).mapper.column_attrs}

            for record in records:
                filtered = {
                    k: v for k, v in record.items()
                    if k in valid_columns and v is not None
                }
                obj = model(**filtered)
                session.add(obj)
                print(f"- Added {key}: {filtered}")

        session.commit()

