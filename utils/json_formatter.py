# Modifies JSON to reconcile visit_id, provider_id, and department_id with ids in SQL tables

from schemas.sql_schema import Provider, Department, Visit, Patient
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import and_
import json

class JSONFormatter:
    def insert_visits_and_resolve_ids(self, session: Session, data: dict) -> dict:
        if not data.get("visit"):
            return data

        llm_to_db_id = {}  # Map LLM visit_id → DB-assigned visit.id
        visit_list = data["visit"]
        new_visit_ids = []

        for visit in visit_list:
            llm_id = visit.get("visit_id")  # This is the temporary LLM-generated id
            visit_obj = Visit(
                patient_id=visit.get("patient_id"),
                visit_date=visit.get("visit_date"),
                visit_type=visit.get("visit_type"),
                department_id=visit.get("department_id"),
                primary_provider_id=visit.get("primary_provider_id"),
                discharge_date=visit.get("discharge_date"),
                created_date=datetime.utcnow()
            )
            session.add(visit_obj)
            session.flush()  # Assigns visit_obj.id

            llm_to_db_id[llm_id] = visit_obj.id
            new_visit_ids.append(visit_obj.id)

        # Replace all visit_id fields across other tables
        def replace_visit_ids(objs):
            for obj in objs:
                if isinstance(obj, dict) and obj.get("visit_id") in llm_to_db_id:
                    obj["visit_id"] = llm_to_db_id[obj["visit_id"]]

        for section in ["symptom", "diagnosis", "medication", "vitalsigns", "labresult", "imagingstudy", "proceduretreatment", "visitnotes"]:
            if section in data:
                replace_visit_ids(data[section])

        # Replace visit objects with just real IDs
        if "visit" in data:
            del data["visit"]

        session.commit()
        return data

    def resolve_providers_and_departments(self, session: Session, data: dict) -> dict:
        provider_cache = {}
        department_cache = {}

        def get_or_create_department(dept_dict):
            if not dept_dict or not isinstance(dept_dict, dict):
                return None
            key = tuple((dept_dict.get("department_name"), dept_dict.get("department_type"), dept_dict.get("system_name")))
            if key in department_cache:
                return department_cache[key]

            dept = session.query(Department).filter(
                and_(
                    Department.department_name == dept_dict.get("department_name"),
                    Department.department_type == dept_dict.get("department_type"),
                    Department.system_name == dept_dict.get("system_name")
                )
            ).first()

            if not dept:
                dept = Department(
                    department_name=dept_dict.get("department_name"),
                    department_type=dept_dict.get("department_type"),
                    system_name=dept_dict.get("system_name"),
                    created_date=datetime.utcnow()
                )
                session.add(dept)
                session.flush()
                print(f"- Added new Department: {dept_dict} with ID {dept.id}")

            department_cache[key] = dept.id
            return dept.id

        def get_or_create_provider(prov_dict):
            if not prov_dict or not isinstance(prov_dict, dict):
                return None

            dept_id = None
            if "department" in prov_dict:
                dept_id = get_or_create_department(prov_dict["department"])
                prov_dict.pop("department", None)

            key = tuple((
                prov_dict.get("provider_name"),
                prov_dict.get("npi_number"),
                prov_dict.get("specialty"),
                dept_id,
                prov_dict.get("active_status", True)
            ))

            if key in provider_cache:
                return provider_cache[key]

            prov = session.query(Provider).filter(
                and_(
                    Provider.provider_name == prov_dict.get("provider_name"),
                    Provider.npi_number == prov_dict.get("npi_number"),
                    Provider.specialty == prov_dict.get("specialty"),
                    Provider.department_id == dept_id,
                    Provider.active_status == prov_dict.get("active_status", True)
                )
            ).first()

            if not prov:
                prov = Provider(
                    provider_name=prov_dict.get("provider_name"),
                    npi_number=prov_dict.get("npi_number"),
                    specialty=prov_dict.get("specialty"),
                    department_id=dept_id,
                    active_status=prov_dict.get("active_status", True),
                    created_date=datetime.utcnow()
                )
                session.add(prov)
                session.flush()
                print(f"- Added new Provider: {prov_dict} with ID {prov.id}")

            provider_cache[key] = prov.id
            return prov.id

        def replace_obj_with_id(obj, key, resolver_func, id_key="id"):
            if key in obj and isinstance(obj[key], dict):
                resolved_id = resolver_func(obj[key])
                obj[f"{key}_id"] = resolved_id
                del obj[key]
                print(f"- Replaced '{key}' object with ID {resolved_id}")

        # 🔁 Replace nested provider/department objects with IDs
        for visit in data.get("visit", []):
            replace_obj_with_id(visit, "primary_provider", get_or_create_provider)
            replace_obj_with_id(visit, "department", get_or_create_department)
            if "visit_notes" in visit:
                replace_obj_with_id(visit["visit_notes"], "author_provider", get_or_create_provider)

        for note in data.get("visitnotes", []):
            replace_obj_with_id(note, "author_provider", get_or_create_provider)

        for diag in data.get("diagnosis", []):
            replace_obj_with_id(diag, "diagnosing_provider", get_or_create_provider)

        for med in data.get("medication", []):
            replace_obj_with_id(med, "prescribing_provider", get_or_create_provider)

        for vital in data.get("vitalsigns", []):
            replace_obj_with_id(vital, "measured_by", get_or_create_provider)

        for lab in data.get("labresult", []):
            replace_obj_with_id(lab, "ordering_provider", get_or_create_provider)

        for img in data.get("imagingstudy", []):
            replace_obj_with_id(img, "ordering_provider", get_or_create_provider)
            replace_obj_with_id(img, "radiologist", get_or_create_provider)

        for proc in data.get("proceduretreatment", []):
            replace_obj_with_id(proc, "primary_provider", get_or_create_provider)

        session.commit()
        return data

    def insert_patient_from_json(self, session: Session, data: dict) -> int:
        """
        Inserts a patient from a JSON dict with structure: { "patient": { ... } }
        """ 
        if "patient" not in data:
            raise ValueError("Missing 'patient' field in input JSON")

        patient_data = data["patient"]
        patient_id = patient_data.get("patient_id")
        mrn = patient_data.get("medical_record_number")

        # Check if patient already exists
        existing = None
        if patient_id:
            existing = session.query(Patient).filter_by(id=patient_id).first()
        elif mrn:
            existing = session.query(Patient).filter_by(medical_record_number=mrn).first()

        if existing:
            print(f"- Patient already exists with ID {existing.id}")
            return existing.id

        # Parse dates
        created_date = patient_data.get("created_date")
        if created_date:
            created_date = datetime.fromisoformat(created_date)

        updated_date = patient_data.get("updated_date")
        if updated_date:
            updated_date = datetime.fromisoformat(updated_date)

        # Create new patient
        new_patient = Patient(
            id=patient_id,
            medical_record_number=mrn,
            created_date=created_date or datetime.utcnow(),
            updated_date=updated_date
        )

        session.add(new_patient)
        session.flush()  # Ensures patient_id is populated
        print(f"- Inserted new patient with ID {new_patient.id}")
        

        session.commit()
        data.pop("patient", None)
        return data
