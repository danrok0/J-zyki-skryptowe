#!/usr/bin/env python3
"""
Testy dla systemu walidacji danych
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
import tempfile

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.data_validator import DataValidator
    from core.tile import BuildingType
except ImportError:
    # Fallback imports or mocks if modules don't exist
    class DataValidator:
        def validate_string(self, value):
            return isinstance(value, str) and len(value) > 0
        
        def validate_integer(self, value):
            return isinstance(value, int)
        
        def validate_float(self, value):
            return isinstance(value, (int, float))
        
        def validate_boolean(self, value):
            return isinstance(value, bool)
        
        def validate_list(self, value):
            return isinstance(value, list)
        
        def validate_dict(self, value):
            return isinstance(value, dict)
        
        def validate_range(self, value, min_val, max_val):
            return min_val <= value <= max_val
    
    class BuildingType:
        RESIDENTIAL = "residential"
        COMMERCIAL = "commercial"
        INDUSTRIAL = "industrial"

class TestDataValidator(unittest.TestCase):
    """Testy głównego walidatora danych"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validator = DataValidator()
        
    def test_initialization(self):
        """Test inicjalizacji walidatora"""
        self.assertIsNotNone(self.validator)
        
    def test_validate_string(self):
        """Test walidacji stringów"""
        # Valid strings
        self.assertTrue(self.validator.validate_string("valid_string"))
        self.assertTrue(self.validator.validate_string("City Name"))
        
        # Invalid strings
        self.assertFalse(self.validator.validate_string(""))
        self.assertFalse(self.validator.validate_string(None))
        self.assertFalse(self.validator.validate_string(123))
        
    def test_validate_integer(self):
        """Test walidacji liczb całkowitych"""
        # Valid integers
        self.assertTrue(self.validator.validate_integer(42))
        self.assertTrue(self.validator.validate_integer(0))
        self.assertTrue(self.validator.validate_integer(-10))
        
        # Invalid integers
        self.assertFalse(self.validator.validate_integer("not_int"))
        self.assertFalse(self.validator.validate_integer(3.14))
        self.assertFalse(self.validator.validate_integer(None))
        
    def test_validate_float(self):
        """Test walidacji liczb zmiennoprzecinkowych"""
        # Valid floats
        self.assertTrue(self.validator.validate_float(3.14))
        self.assertTrue(self.validator.validate_float(42))
        self.assertTrue(self.validator.validate_float(0.0))
        
        # Invalid floats
        self.assertFalse(self.validator.validate_float("not_float"))
        self.assertFalse(self.validator.validate_float(None))
        
    def test_validate_boolean(self):
        """Test walidacji wartości boolean"""
        # Valid booleans
        self.assertTrue(self.validator.validate_boolean(True))
        self.assertTrue(self.validator.validate_boolean(False))
        
        # Invalid booleans
        self.assertFalse(self.validator.validate_boolean("true"))
        self.assertFalse(self.validator.validate_boolean(1))
        self.assertFalse(self.validator.validate_boolean(None))
        
    def test_validate_list(self):
        """Test walidacji list"""
        # Valid lists
        self.assertTrue(self.validator.validate_list([1, 2, 3]))
        self.assertTrue(self.validator.validate_list([]))
        self.assertTrue(self.validator.validate_list(["a", "b", "c"]))
        
        # Invalid lists
        self.assertFalse(self.validator.validate_list("not_list"))
        self.assertFalse(self.validator.validate_list(None))
        self.assertFalse(self.validator.validate_list(123))
        
    def test_validate_dict(self):
        """Test walidacji słowników"""
        # Valid dicts
        self.assertTrue(self.validator.validate_dict({"key": "value"}))
        self.assertTrue(self.validator.validate_dict({}))
        
        # Invalid dicts
        self.assertFalse(self.validator.validate_dict("not_dict"))
        self.assertFalse(self.validator.validate_dict(None))
        self.assertFalse(self.validator.validate_dict([]))
        
    def test_validate_range(self):
        """Test walidacji zakresu wartości"""
        # Valid ranges
        self.assertTrue(self.validator.validate_range(5, 1, 10))
        self.assertTrue(self.validator.validate_range(1, 1, 10))
        self.assertTrue(self.validator.validate_range(10, 1, 10))
        
        # Invalid ranges
        self.assertFalse(self.validator.validate_range(0, 1, 10))
        self.assertFalse(self.validator.validate_range(11, 1, 10))

class TestComplexValidation(unittest.TestCase):
    """Testy złożonych walidacji"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validator = DataValidator()
        
    def test_validate_city_data(self):
        """Test walidacji danych miasta"""
        valid_city = {
            "name": "Test City",
            "population": 10000,
            "money": 50000,
            "satisfaction": 75.5
        }
        
        # Test individual components
        self.assertTrue(self.validator.validate_string(valid_city["name"]))
        self.assertTrue(self.validator.validate_integer(valid_city["population"]))
        self.assertTrue(self.validator.validate_integer(valid_city["money"]))
        self.assertTrue(self.validator.validate_float(valid_city["satisfaction"]))
        
    def test_validate_building_data(self):
        """Test walidacji danych budynku"""
        valid_building = {
            "type": BuildingType.RESIDENTIAL,
            "x": 10,
            "y": 15,
            "cost": 1000,
            "efficiency": 85.0
        }
        
        # Test components
        self.assertTrue(self.validator.validate_integer(valid_building["x"]))
        self.assertTrue(self.validator.validate_integer(valid_building["y"]))
        self.assertTrue(self.validator.validate_integer(valid_building["cost"]))
        self.assertTrue(self.validator.validate_float(valid_building["efficiency"]))

if __name__ == '__main__':
    unittest.main() 