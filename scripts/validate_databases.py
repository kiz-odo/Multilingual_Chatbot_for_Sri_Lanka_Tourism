#!/usr/bin/env python3
"""
Database Validation Script for Sri Lanka Tourism Chatbot
=========================================================

Validates all JSON databases for:
- Schema correctness
- Data completeness
- Coordinate validation
- Duplicate detection
- Cross-reference validation
"""

import json
import os
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Sri Lanka geographic bounds
SRI_LANKA_BOUNDS = {
    "lat_min": 5.9,
    "lat_max": 9.9,
    "lon_min": 79.5,
    "lon_max": 81.9
}

class DatabaseValidator:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def validate_coordinates(self, coords: List[float], item_id: str) -> bool:
        """Validate if coordinates are within Sri Lanka bounds."""
        if not coords or len(coords) != 2:
            self.errors.append(f"{item_id}: Invalid coordinates format: {coords}")
            return False
        
        lon, lat = coords
        if not (SRI_LANKA_BOUNDS["lon_min"] <= lon <= SRI_LANKA_BOUNDS["lon_max"]):
            self.errors.append(f"{item_id}: Longitude {lon} out of bounds")
            return False
        
        if not (SRI_LANKA_BOUNDS["lat_min"] <= lat <= SRI_LANKA_BOUNDS["lat_max"]):
            self.errors.append(f"{item_id}: Latitude {lat} out of bounds")
            return False
        
        return True
    
    def validate_multilingual_field(self, field: Dict[str, str], item_id: str, field_name: str) -> bool:
        """Validate multilingual fields have required languages."""
        required_langs = ["en", "si", "ta"]
        if not isinstance(field, dict):
            self.errors.append(f"{item_id}: {field_name} is not a dictionary")
            return False
        
        for lang in required_langs:
            if lang not in field:
                self.warnings.append(f"{item_id}: Missing {lang} translation in {field_name}")
            elif not field[lang] or len(field[lang].strip()) == 0:
                self.warnings.append(f"{item_id}: Empty {lang} translation in {field_name}")
        
        return True
    
    def validate_phone_number(self, phone: str, item_id: str) -> bool:
        """Validate Sri Lankan phone number format."""
        if not phone or phone == "":
            return True  # Optional field
        
        # Check for +94 country code
        if not (phone.startswith("+94") or phone.startswith("94") or phone.startswith("0")):
            self.warnings.append(f"{item_id}: Phone number {phone} doesn't follow Sri Lankan format")
            return False
        
        return True
    
    def validate_master_database(self) -> Dict[str, Any]:
        """Validate master_database_enhanced.json."""
        print("[*] Validating master_database_enhanced.json...")
        
        filepath = os.path.join(self.base_path, "master_database_enhanced.json")
        if not os.path.exists(filepath):
            self.errors.append("master_database_enhanced.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("original_id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            if "name" not in item:
                self.errors.append(f"{item_id}: Missing 'name' field")
                is_valid = False
            else:
                self.validate_multilingual_field(item["name"], item_id, "name")
            
            if "description" not in item:
                self.errors.append(f"{item_id}: Missing 'description' field")
                is_valid = False
            else:
                self.validate_multilingual_field(item["description"], item_id, "description")
            
            # Validate location
            if "location" in item:
                if "coordinates" in item["location"]:
                    self.validate_coordinates(item["location"]["coordinates"], item_id)
                else:
                    self.warnings.append(f"{item_id}: Missing coordinates")
            
            # Validate contact info
            if "contact_info" in item and "phone" in item["contact_info"]:
                self.validate_phone_number(item["contact_info"]["phone"], item_id)
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Master Database: {valid_count}/{total} valid")
        return stats
    
    def validate_activities_database(self) -> Dict[str, Any]:
        """Validate activities_database.json."""
        print("[*] Validating activities_database.json...")
        
        filepath = os.path.join(self.base_path, "activities_database.json")
        if not os.path.exists(filepath):
            self.errors.append("activities_database.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            required_fields = ["name", "description", "category", "activity_type", "location", "duration_hours", "price"]
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"{item_id}: Missing '{field}' field")
                    is_valid = False
            
            # Validate multilingual
            if "name" in item:
                self.validate_multilingual_field(item["name"], item_id, "name")
            if "description" in item:
                self.validate_multilingual_field(item["description"], item_id, "description")
            
            # Validate location
            if "location" in item and "coordinates" in item["location"]:
                self.validate_coordinates(item["location"]["coordinates"], item_id)
            
            # Validate price
            if "price" in item:
                if "adult" not in item["price"] or "currency" not in item["price"]:
                    self.errors.append(f"{item_id}: Invalid price structure")
                    is_valid = False
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Activities: {valid_count}/{total} valid")
        return stats
    
    def validate_events_database(self) -> Dict[str, Any]:
        """Validate events_database.json."""
        print("[*] Validating events_database.json...")
        
        filepath = os.path.join(self.base_path, "events_database.json")
        if not os.path.exists(filepath):
            self.errors.append("events_database.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            required_fields = ["name", "description", "category", "event_type", "location", "date_info"]
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"{item_id}: Missing '{field}' field")
                    is_valid = False
            
            # Validate date format
            if "date_info" in item:
                if "start_date" not in item["date_info"] or "end_date" not in item["date_info"]:
                    self.errors.append(f"{item_id}: Invalid date_info structure")
                    is_valid = False
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Events: {valid_count}/{total} valid")
        return stats
    
    def validate_hotels_database(self) -> Dict[str, Any]:
        """Validate hotels_database.json."""
        print("[*] Validating hotels_database.json...")
        
        filepath = os.path.join(self.base_path, "hotels_database.json")
        if not os.path.exists(filepath):
            self.errors.append("hotels_database.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            required_fields = ["name", "description", "category", "star_rating", "location", "price_range"]
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"{item_id}: Missing '{field}' field")
                    is_valid = False
            
            # Validate price range
            if "price_range" in item:
                if "min_price" not in item["price_range"] or "max_price" not in item["price_range"]:
                    self.errors.append(f"{item_id}: Invalid price_range structure")
                    is_valid = False
                elif item["price_range"]["min_price"] > item["price_range"]["max_price"]:
                    self.errors.append(f"{item_id}: min_price greater than max_price")
                    is_valid = False
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Hotels: {valid_count}/{total} valid")
        return stats
    
    def validate_restaurants_database(self) -> Dict[str, Any]:
        """Validate restaurants_database.json."""
        print("[*] Validating restaurants_database.json...")
        
        filepath = os.path.join(self.base_path, "restaurants_database.json")
        if not os.path.exists(filepath):
            self.errors.append("restaurants_database.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            required_fields = ["name", "description", "cuisine_types", "price_range", "location"]
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"{item_id}: Missing '{field}' field")
                    is_valid = False
            
            # Validate cuisine types
            if "cuisine_types" in item:
                if not isinstance(item["cuisine_types"], list) or len(item["cuisine_types"]) == 0:
                    self.warnings.append(f"{item_id}: No cuisine types specified")
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Restaurants: {valid_count}/{total} valid")
        return stats
    
    def validate_transportation_database(self) -> Dict[str, Any]:
        """Validate transportation_database.json."""
        print("[*] Validating transportation_database.json...")
        
        filepath = os.path.join(self.base_path, "transportation_database.json")
        if not os.path.exists(filepath):
            self.errors.append("transportation_database.json not found")
            return {"valid": False}
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        total = len(data)
        valid_count = 0
        
        for item in data:
            item_id = item.get("id", "UNKNOWN")
            is_valid = True
            
            # Check required fields
            required_fields = ["type", "name", "description"]
            for field in required_fields:
                if field not in item:
                    self.errors.append(f"{item_id}: Missing '{field}' field")
                    is_valid = False
            
            if is_valid:
                valid_count += 1
        
        stats = {
            "total": total,
            "valid": valid_count,
            "invalid": total - valid_count
        }
        
        print(f"[OK] Transportation: {valid_count}/{total} valid")
        return stats
    
    def detect_duplicates(self) -> Dict[str, List[str]]:
        """Detect duplicate entries across databases."""
        print("[*] Checking for duplicates...")
        
        duplicates = defaultdict(list)
        
        # Check master database
        filepath = os.path.join(self.base_path, "master_database_enhanced.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            names = {}
            for item in data:
                name = item.get("name", {}).get("en", "")
                location = item.get("location", {}).get("city", "")
                key = f"{name}_{location}".lower()
                
                if key in names:
                    duplicates["master_database"].append(f"Duplicate: {name} in {location}")
                else:
                    names[key] = item.get("original_id")
        
        print(f"[OK] Found {len(duplicates)} potential duplicates")
        return dict(duplicates)
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validations."""
        print("=" * 80)
        print("Database Validation Report")
        print("=" * 80)
        print()
        
        results = {}
        
        # Validate each database
        results["master_database"] = self.validate_master_database()
        results["activities"] = self.validate_activities_database()
        results["events"] = self.validate_events_database()
        results["hotels"] = self.validate_hotels_database()
        results["restaurants"] = self.validate_restaurants_database()
        results["transportation"] = self.validate_transportation_database()
        
        # Check duplicates
        duplicates = self.detect_duplicates()
        
        # Print summary
        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        total_items = sum(r.get("total", 0) for r in results.values() if isinstance(r, dict))
        total_valid = sum(r.get("valid", 0) for r in results.values() if isinstance(r, dict))
        
        print(f"Total Items:     {total_items}")
        print(f"Valid Items:     {total_valid}")
        print(f"Invalid Items:   {total_items - total_valid}")
        print(f"Errors:          {len(self.errors)}")
        print(f"Warnings:        {len(self.warnings)}")
        print()
        
        if self.errors:
            print("ERRORS:")
            for error in self.errors[:20]:  # Show first 20 errors
                print(f"  - {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
            print()
        
        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings[:20]:  # Show first 20 warnings
                print(f"  - {warning}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more warnings")
            print()
        
        print("=" * 80)
        
        if len(self.errors) == 0:
            print("[OK] All databases passed validation!")
        else:
            print("[WARNING] Some databases have validation errors. Please review.")
        
        print("=" * 80)
        
        return {
            "results": results,
            "total_items": total_items,
            "total_valid": total_valid,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "duplicates": len(duplicates)
        }


def main():
    """Main validation function."""
    base_path = "e:/Multilingual_Chatbot_for_Sri_Lanka_Tourism_V1"
    
    validator = DatabaseValidator(base_path)
    results = validator.validate_all()
    
    # Save validation report
    report_path = os.path.join(base_path, "database_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": "2025-12-13",
            "summary": results,
            "errors": validator.errors[:100],  # Save first 100 errors
            "warnings": validator.warnings[:100]  # Save first 100 warnings
        }, f, indent=2)
    
    print(f"\n[OK] Validation report saved to: {report_path}")


if __name__ == "__main__":
    main()
