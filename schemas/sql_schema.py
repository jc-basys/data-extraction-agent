# Reference Relational Database Schema Here: https://dbdiagram.io/d/Database-Schema-Smart-EMR-685e4192f413ba350825a2dc

from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    medical_record_number = Column(String(50), unique=True, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True)

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True)
    provider_name = Column(String(100), nullable=True)
    npi_number = Column(String(20), unique=True, nullable=True)
    specialty = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    active_status = Column(Boolean, default=True, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    department_name = Column(String(100), nullable=True)
    department_type = Column(String(50), nullable=True)
    system_name = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_date = Column(String(20), nullable=True)
    visit_type = Column(String(50), nullable=True)
    primary_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    discharge_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class VisitNotes(Base):
    __tablename__ = "visit_notes"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    note_date = Column(String(20), nullable=True)
    note_type = Column(String(50), nullable=True)
    full_note_text = Column(Text, nullable=True)
    chief_complaint = Column(Text, nullable=True)
    history_present_illness = Column(Text, nullable=True)
    review_of_systems = Column(Text, nullable=True)
    physical_exam = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    author_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    extraction_method = Column(String(50), nullable=True)
    extraction_timestamp = Column(String(50), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    diagnosis_name = Column(String(100), nullable=True)
    icd10_code = Column(String(20), nullable=True)
    onset_date = Column(String(20), nullable=True)
    resolution_date = Column(String(20), nullable=True)
    is_chronic = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    severity = Column(String(50), nullable=True)
    diagnosing_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    diagnosis_source = Column(String(50), nullable=True)
    diagnosis_context = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    updated_date = Column(String(20), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    symptom_name = Column(String(100), nullable=True)
    onset_date = Column(String(20), nullable=True)
    duration = Column(String(50), nullable=True)
    frequency = Column(String(50), nullable=True)
    severity = Column(String(50), nullable=True)
    symptom_description = Column(Text, nullable=True)
    alleviating_factors = Column(Text, nullable=True)
    aggravating_factors = Column(Text, nullable=True)
    reported_date = Column(String(20), nullable=True)
    resolution_date = Column(String(20), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    medication_name = Column(String(100), nullable=True)
    generic_name = Column(String(100), nullable=True)
    rxnorm_code = Column(String(50), nullable=True)
    dose = Column(String(50), nullable=True)
    dose_unit = Column(String(20), nullable=True)
    frequency = Column(String(50), nullable=True)
    route = Column(String(50), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    discontinuation_reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_prn = Column(Boolean, default=False)
    prescribing_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    sig_text = Column(Text, nullable=True)
    patient_instructions = Column(Text, nullable=True)
    updated_date = Column(String(20), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class VitalSigns(Base):
    __tablename__ = "vital_signs"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    measurement_datetime = Column(String(20), nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    pulse_bpm = Column(Integer, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    temperature_celsius = Column(Float, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    oxygen_saturation_percent = Column(Integer, nullable=True)
    pain_scale = Column(Integer, nullable=True)
    additional_vitals = Column(Text, nullable=True)
    measurement_context = Column(String(50), nullable=True)
    measured_by_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    lab_name = Column(String(100), nullable=True)
    test_name = Column(String(100), nullable=True)
    loinc_code = Column(String(50),  nullable=True)
    result_value = Column(String(100), nullable=True)
    result_numeric = Column(Float,  nullable=True)
    unit_of_measurement = Column(String(50), nullable=True)
    reference_range_low = Column(Float,  nullable=True)
    reference_range_high = Column(Float, nullable=True)
    reference_range_text = Column(String(100),  nullable=True)
    abnormality_flag = Column(Boolean, default=False,  nullable=True)
    abnormality_type = Column(String(50), nullable=True)
    collection_datetime = Column(String(20), nullable=True)
    result_datetime = Column(String(20), nullable=True)
    ordering_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    result_status = Column(String(50), nullable=True)
    clinical_significance = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

class ImagingStudy(Base):
    __tablename__ = "imaging_studies"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    imaging_type = Column(String(50), nullable=True)
    modality = Column(String(50), nullable=True)
    body_region = Column(String(100), nullable=True)
    study_datetime = Column(String(20), nullable=True)
    ordering_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    radiologist_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    indication = Column(Text, nullable=True)
    technique = Column(Text, nullable=True)
    comparison = Column(Text, nullable=True)
    findings = Column(Text, nullable=True)
    impression = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    report_status = Column(String(50), nullable=True)
    critical_findings = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)

class ProcedureTreatment(Base):
    __tablename__ = "procedure_treatments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    procedure_name = Column(String(100), nullable=True)
    procedure_type = Column(String(50), nullable=True)
    cpt_code = Column(String(50), nullable=True)
    procedure_date = Column(String(20), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    outcome = Column(Text, nullable=True)
    outcome_details = Column(Text, nullable=True)
    complications = Column(Text, nullable=True)
    primary_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    therapy_type = Column(String(50), nullable=True)
    sessions_completed = Column(Integer, nullable=True)
    sessions_planned = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
