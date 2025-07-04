# Import Packages
import os
import json
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

# Set API Keys
LANDING_AI_API_KEY = ""
GOOGLE_API_KEY = ""

os.environ["VISION_AGENT_API_KEY"] = LANDING_AI_API_KEY

# Import functions
from schemas.json_schemas import *
from tools.scrape_doc import PDFScraper
from utils.json_prompt_gen import JSONPromptGen
from tools.analyze_doc import DocAnalyzer
from utils.json_validator import JSONValidator
from utils.json_formatter import JSONFormatter
from schemas.sql_schema import Base
from utils.save_to_sql import SQLSaver

def main():
    # User defined patient id, filepaths, and database config
    patient_id = 0123456
    pdf_input_filepath = r""              # .pdf file
    scrape_output_filepath = r""          # .txt file
    json_output_filepath = r""            # .txt file
    
    db_config = {
        "username":        "",
        "password":        "",
        "database_name":   ""
    }

    run_pipeline(patient_id, pdf_input_filepath, scrape_output_filepath, json_output_filepath, db_config)

def run_pipeline(patient_id, pdf_input_filepath, scrape_output_filepath, json_output_filepath, db_config):
    schemas = {
                Patient: False, 
                Visit: True, 
                VisitNotes: True, 
                Diagnosis: True, 
                Symptom: True, 
                Medication: True, 
                VitalSigns: True, 
                LabResult: True, 
                ImagingStudy: True, 
                ProcedureTreatment: True
            }

    # Generate JSON template for use in prompt based on schemas
    Generator = JSONPromptGen()
    json_prompt = Generator.generate_json_prompt(schemas, patient_id)

    # Scrape pdf document
    Scraper = PDFScraper()
    scraped_text = Scraper.extract_text_from_pdf_landingai(pdf_input_filepath)
    print("Scraped pdf successfully")
    print(f"Content preview: {str(scraped_text)[:500]}...")

    if scrape_output_filepath != "":
        try:
            with open(scrape_output_filepath, "w", encoding="utf-8") as f:
                    f.write(json.dumps(scraped_text, indent=2, default=str))
                    print("Scraped text saved sucessfully")
        except:
            print("Error saving scraped output to .txt file.")

    # Prompt LLM to analyze text
    Analyzer = DocAnalyzer(GOOGLE_API_KEY)
    chunks = Analyzer.chunk_text(scraped_text)
    results = Analyzer.ask_questions_on_chunks(chunks, patient_id, json_prompt)
    results_json = json.loads(results)
    print("AI Based Analysis Sucessful")

    # Validate JSON output format using original Pydantic Schemas. Pipeline will attempt to continue regardless but this can provide helpful info in case of failure.
    Validator = JSONValidator()
    all_valid, validation_notes = Validator.validate_json_sections(schemas, results_json)
    print("Pydantic Check for JSON Format:\n", json.dumps({k.__name__: v for k, v in validation_notes.items()}, indent=2))

    # Define Schema for JSON to SQL mapping (note: provider and department are not needed as they are added separately)
    schemas = {
        "patient": Patient,           
        "visit": Visit,               
        "visitnotes": VisitNotes,     
        "diagnosis": Diagnosis,
        "symptom": Symptom,
        "medication": Medication,
        "vitalsigns": VitalSigns,
        "labresult": LabResult,
        "imagingstudy": ImagingStudy,
        "proceduretreatment": ProcedureTreatment,
    }

    # Extract relevant parameters for database 
    username = db_config.get('username')
    password = db_config.get('password')
    database_name = db_config.get('database_name')

    # Create Database
    engine = create_engine(url=f"mysql+pymysql://{username}:{password}@localhost")
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database_name}`"))
        conn.commit()

    # Create Tables
    engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost/{database_name}")
    Base.metadata.create_all(engine)
    print("Database and table creation successful.")

    # Define Session and Input
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Preprocessing step to reconcile foreign keys (patient_id, provider_ids (multiple), department_ids (multiple), and visit_ids (multiple)) 
        Formatter = JSONFormatter()
        Formatter.insert_patient_from_json(session, results_json)
        updated_data = Formatter.resolve_providers_and_departments(session, results_json)
        updated_data = Formatter.insert_visits_and_resolve_ids(session, updated_data)
        
        # Save all JSONs to database
        Saver = SQLSaver()
        Saver.insert_non_patient_entities(session,updated_data)
        print("Data saved succesfully")
        
if __name__ == "__main__":
     main()