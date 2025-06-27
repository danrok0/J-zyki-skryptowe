#!/usr/bin/env python3
"""
Testy dla systemu walidacji
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.validation_system import ValidationSystem, ValidationResult
from core.tile import BuildingType
from core.game_engine import GameEngine

class TestValidationSystem(unittest.TestCase):
    """Testy głównego systemu walidacji"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        self.mock_game_engine = Mock(spec=GameEngine)
        
    def test_initialization(self):
        """Test inicjalizacji systemu walidacji"""
        self.assertIsNotNone(self.validation_system.patterns)
        self.assertIsNotNone(self.validation_system.limits)
        self.assertIn('city_name', self.validation_system.patterns)
        self.assertIn('money', self.validation_system.limits)
        
    def test_validate_input_data_success(self):
        """Test pomyślnej walidacji danych wejściowych"""
        data = {"city_name": "Warsaw", "population": "1000"}
        schema = {"city_name": "city_name_required", "population": "population"}
        
        result = self.validation_system.validate_input_data(data, schema)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
    def test_validate_input_data_failure(self):
        """Test nieudanej walidacji"""
        data = {"city_name": "", "population": "-100"}
        schema = {"city_name": "city_name_required", "population": "population"}
        
        result = self.validation_system.validate_input_data(data, schema)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

class TestBuildingValidation(unittest.TestCase):
    """Testy walidacji budynków"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_building_data_valid(self):
        """Test poprawnych danych budynku"""
        building_data = {
            'name': 'Test Building',
            'cost': 1000,
            'x': 5,
            'y': 5,
            'type': 'residential'
        }
        
        result = self.validation_system.validate_building_data(building_data)
        self.assertTrue(result.is_valid)
        
    def test_validate_building_data_invalid_cost(self):
        """Test niepoprawnego kosztu budynku"""
        building_data = {
            'name': 'Test Building',
            'cost': -100,  # Negative cost
            'x': 5,
            'y': 5,
            'type': 'residential'
        }
        
        result = self.validation_system.validate_building_data(building_data)
        self.assertFalse(result.is_valid)
        
    def test_validate_coordinates(self):
        """Test walidacji współrzędnych"""
        # Valid coordinates
        result = self.validation_system.validate_coordinates(10, 15, 50, 50)
        self.assertTrue(result.is_valid)
        
        # Invalid coordinates (out of bounds)
        result = self.validation_system.validate_coordinates(-1, 5, 50, 50)
        self.assertFalse(result.is_valid)
        
    def test_validate_building_placement(self):
        """Test walidacji umieszczenia budynku"""
        building_data = {'size': (1, 1), 'type': 'residential'}
        
        # Valid placement
        result = self.validation_system.validate_building_placement(5, 5, building_data, 50, 50)
        self.assertTrue(result.is_valid)
        
        # Invalid placement (out of bounds)
        result = self.validation_system.validate_building_placement(49, 49, building_data, 50, 50)
        self.assertFalse(result.is_valid)

class TestMoneyValidation(unittest.TestCase):
    """Testy walidacji pieniędzy"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_money_amount_valid(self):
        """Test poprawnej kwoty pieniędzy"""
        result = self.validation_system.validate_money_amount(1000)
        self.assertTrue(result.is_valid)
        
        result = self.validation_system.validate_money_amount(-500)  # Negative allowed
        self.assertTrue(result.is_valid)
        
    def test_validate_money_amount_invalid(self):
        """Test niepoprawnej kwoty pieniędzy"""
        result = self.validation_system.validate_money_amount("not_a_number")
        self.assertFalse(result.is_valid)
        
    def test_validate_tax_rate(self):
        """Test walidacji stawki podatkowej"""
        # Valid tax rates
        result = self.validation_system.validate_tax_rate(0.15)
        self.assertTrue(result.is_valid)
        
        result = self.validation_system.validate_tax_rate(0.5)
        self.assertTrue(result.is_valid)
        
        # Invalid tax rates
        result = self.validation_system.validate_tax_rate(-0.1)
        self.assertFalse(result.is_valid)
        
        result = self.validation_system.validate_tax_rate(1.5)
        self.assertFalse(result.is_valid)

class TestPopulationValidation(unittest.TestCase):
    """Testy walidacji populacji"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_population_valid(self):
        """Test poprawnej populacji"""
        result = self.validation_system.validate_population(5000)
        self.assertTrue(result.is_valid)
        
        result = self.validation_system.validate_population(0)
        self.assertTrue(result.is_valid)
        
    def test_validate_population_invalid(self):
        """Test niepoprawnej populacji"""
        result = self.validation_system.validate_population(-100)
        self.assertFalse(result.is_valid)
        
        result = self.validation_system.validate_population("not_a_number")
        self.assertFalse(result.is_valid)

class TestFileValidation(unittest.TestCase):
    """Testy walidacji plików"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_save_filename(self):
        """Test walidacji nazwy pliku zapisu"""
        # Valid filenames
        result = self.validation_system.validate_save_filename("my_city_save")
        self.assertTrue(result.is_valid)
        
        result = self.validation_system.validate_save_filename("City-Save_01")
        self.assertTrue(result.is_valid)
        
    def test_validate_save_filename_invalid(self):
        """Test niepoprawnych nazw plików"""
        # Invalid characters
        result = self.validation_system.validate_save_filename("save@#$")
        self.assertFalse(result.is_valid)
        
        # Too long
        result = self.validation_system.validate_save_filename("a" * 100)
        self.assertFalse(result.is_valid)

class TestGameSaveValidation(unittest.TestCase):
    """Testy walidacji zapisów gry"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_game_save_data_valid(self):
        """Test poprawnych danych zapisu gry"""
        save_data = {
            'city_name': 'Test City',
            'money': 10000,
            'population': 1000,
            'turn': 50,
            'city_level': 3
        }
        
        result = self.validation_system.validate_game_save_data(save_data)
        self.assertTrue(result.is_valid)
        
    def test_validate_game_save_data_invalid(self):
        """Test niepoprawnych danych zapisu"""
        save_data = {
            'city_name': '',  # Empty name
            'money': "not_a_number",
            'population': -100  # Negative population
        }
        
        result = self.validation_system.validate_game_save_data(save_data)
        self.assertFalse(result.is_valid)
        
class TestEconomicValidation(unittest.TestCase):
    """Testy walidacji danych ekonomicznych"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.validation_system = ValidationSystem()
        
    def test_validate_economic_data_valid(self):
        """Test poprawnych danych ekonomicznych"""
        economy_data = {
            'income': 1000,
            'expenses': 800,
            'tax_rate': 0.15,
            'balance': 200
        }
        
        result = self.validation_system.validate_economic_data(economy_data)
        self.assertTrue(result.is_valid)
        
    def test_validate_economic_data_invalid(self):
        """Test niepoprawnych danych ekonomicznych"""
        economy_data = {
            'income': -100,  # Negative income
            'tax_rate': 1.5  # Tax rate > 100%
        }
        
        result = self.validation_system.validate_economic_data(economy_data)
        self.assertFalse(result.is_valid)

if __name__ == '__main__':
    unittest.main() 