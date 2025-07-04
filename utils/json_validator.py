# Validates JSON object using Pydantic schema 

from typing import List, Type, Dict, Any
from pydantic import BaseModel, ValidationError

class JSONValidator:
    def validate_json_sections(
        self,
        schemas: Dict[str, Type[BaseModel]],
        data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        results = {}
        all_valid = True
        for section_key, schema in schemas.items():
            results[section_key] = {"valid": [], "errors": []}
            items = data.get(section_key, [])
            if not isinstance(items, list):
                results[section_key]["errors"].append({
                    "index": None,
                    "errors": f"Expected a list of objects for section '{section_key}', got {type(items)}"
                })
                continue

            for idx, item in enumerate(items):
                try:
                    validated = schema.parse_obj(item)
                    results[section_key]["valid"].append(validated.dict())
                except ValidationError as ve:
                    results[section_key]["errors"].append({
                        "index": idx,
                        "errors": ve.errors()
                    }
                    )
                    all_valid = False

        return all_valid, results
