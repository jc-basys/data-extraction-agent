# Data Extraction Agent

This repository contains code for a Data Extraction Agent that converts scanned medical record pdfs into smart medical records. Text from the pdf is first scraped and fed through an LLM pipeline before being saved to a relational database. This implementation harnesses Python / MySQL in addition to the following:
- LandingAI Document Extractor
- Pydantic
- LangChain
- Gemini 2.5 Flash
- SQLAlchemy

To run this repository:
- Install relevant libraries using requirements.txt.
- Ensure that MySQL Workbench and MySQL Shell are installed and configured.
- Insert user defined fields in main.py (API Keys, filepaths, patient_id, and database_config parameters)
- Run main.py.

Contributors:
- Jayden Chen (project owner)
- Smruti Patil
- Akshat Srivastava
- Mariam Abu-Rahma
- Amina Tasleem
