#!/usr/bin/env python3
"""
Testy dla systemu raportów
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reports import (
    ReportManager, FinancialReport, PopulationReport, BuildingReport,
    ResourceReport, PerformanceReport, ReportType, ReportFormat
)
from core.game_engine import GameEngine

class TestReportManager(unittest.TestCase):
    """Testy zarządcy raportów"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.report_manager = ReportManager()
        self.mock_game_engine = Mock(spec=GameEngine)
        
    def test_initialization(self):
        """Test inicjalizacji zarządcy raportów"""
        self.assertIsNotNone(self.report_manager)
        self.assertEqual(len(self.report_manager.reports_history), 0)
        
    def test_generate_financial_report(self):
        """Test generowania raportu finansowego"""
        # Mock engine data
        self.mock_game_engine.resources.money = 10000
        self.mock_game_engine.get_total_income.return_value = 1500
        self.mock_game_engine.get_total_expenses.return_value = 1200
        
        report = self.report_manager.generate_report(
            ReportType.FINANCIAL, self.mock_game_engine
        )
        
        self.assertIsInstance(report, FinancialReport)
        self.assertEqual(report.current_money, 10000)
        
    def test_generate_population_report(self):
        """Test generowania raportu populacji"""
        self.mock_game_engine.population.get_total_population.return_value = 5000
        self.mock_game_engine.population.get_satisfaction.return_value = 75
        self.mock_game_engine.population.get_unemployment_rate.return_value = 8.5
        
        report = self.report_manager.generate_report(
            ReportType.POPULATION, self.mock_game_engine
        )
        
        self.assertIsInstance(report, PopulationReport)
        self.assertEqual(report.total_population, 5000)
        self.assertEqual(report.satisfaction, 75)
        
    def test_generate_building_report(self):
        """Test generowania raportu budynków"""
        mock_buildings = [
            Mock(building_type='residential', condition=90),
            Mock(building_type='commercial', condition=85),
            Mock(building_type='industrial', condition=95)
        ]
        self.mock_game_engine.get_all_buildings.return_value = mock_buildings
        
        report = self.report_manager.generate_report(
            ReportType.BUILDINGS, self.mock_game_engine
        )
        
        self.assertIsInstance(report, BuildingReport)
        self.assertEqual(len(report.buildings_by_type), 3)
        
    def test_generate_resource_report(self):
        """Test generowania raportu zasobów"""
        self.mock_game_engine.resources.power = 850
        self.mock_game_engine.resources.water = 920
        self.mock_game_engine.get_power_consumption.return_value = 800
        self.mock_game_engine.get_water_consumption.return_value = 900
        
        report = self.report_manager.generate_report(
            ReportType.RESOURCES, self.mock_game_engine
        )
        
        self.assertIsInstance(report, ResourceReport)
        self.assertEqual(report.power_available, 850)
        self.assertEqual(report.water_available, 920)
        
    def test_save_report_history(self):
        """Test zapisywania historii raportów"""
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200
        )
        
        self.report_manager.save_to_history(report)
        self.assertEqual(len(self.report_manager.reports_history), 1)
        
    def test_export_report_json(self):
        """Test eksportu raportu do JSON"""
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200
        )
        
        with patch('builtins.open', create=True) as mock_open:
            result = self.report_manager.export_report(
                report, ReportFormat.JSON, "test_report.json"
            )
            self.assertTrue(result)
            
    def test_export_report_csv(self):
        """Test eksportu raportu do CSV"""
        report = PopulationReport(
            total_population=5000,
            satisfaction=75,
            unemployment_rate=8.5
        )
        
        with patch('builtins.open', create=True) as mock_open:
            result = self.report_manager.export_report(
                report, ReportFormat.CSV, "test_report.csv"
            )
            self.assertTrue(result)

class TestFinancialReport(unittest.TestCase):
    """Testy raportu finansowego"""
    
    def test_financial_report_creation(self):
        """Test tworzenia raportu finansowego"""
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200,
            net_income=300
        )
        
        self.assertEqual(report.current_money, 10000)
        self.assertEqual(report.total_income, 1500)
        self.assertEqual(report.total_expenses, 1200)
        self.assertEqual(report.net_income, 300)
        
    def test_financial_report_calculations(self):
        """Test obliczeń w raporcie finansowym"""
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200
        )
        
        # Auto-calculate net income
        self.assertEqual(report.get_net_income(), 300)
        
    def test_financial_report_to_dict(self):
        """Test konwersji raportu finansowego do słownika"""
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200
        )
        
        data = report.to_dict()
        self.assertIn('current_money', data)
        self.assertIn('total_income', data)
        self.assertIn('total_expenses', data)
        
    def test_financial_trends_calculation(self):
        """Test obliczania trendów finansowych"""
        historical_data = [
            {'net_income': 200, 'date': '2024-01-01'},
            {'net_income': 250, 'date': '2024-01-02'},
            {'net_income': 300, 'date': '2024-01-03'}
        ]
        
        report = FinancialReport(
            current_money=10000,
            total_income=1500,
            total_expenses=1200
        )
        
        trend = report.calculate_trend(historical_data)
        self.assertGreater(trend, 0)  # Pozytywny trend

class TestPopulationReport(unittest.TestCase):
    """Testy raportu populacji"""
    
    def test_population_report_creation(self):
        """Test tworzenia raportu populacji"""
        report = PopulationReport(
            total_population=5000,
            satisfaction=75,
            unemployment_rate=8.5,
            growth_rate=2.3
        )
        
        self.assertEqual(report.total_population, 5000)
        self.assertEqual(report.satisfaction, 75)
        self.assertEqual(report.unemployment_rate, 8.5)
        
    def test_population_demographics(self):
        """Test demografii populacji"""
        demographics = {
            'children': 1000,
            'adults': 3000,
            'elderly': 1000
        }
        
        report = PopulationReport(
            total_population=5000,
            satisfaction=75,
            unemployment_rate=8.5,
            demographics=demographics
        )
        
        self.assertEqual(report.demographics['adults'], 3000)
        
    def test_population_predictions(self):
        """Test predykcji populacji"""
        report = PopulationReport(
            total_population=5000,
            satisfaction=75,
            unemployment_rate=8.5,
            growth_rate=2.3
        )
        
        prediction = report.predict_population(12)  # 12 miesięcy
        self.assertGreater(prediction, 5000)

class TestBuildingReport(unittest.TestCase):
    """Testy raportu budynków"""
    
    def test_building_report_creation(self):
        """Test tworzenia raportu budynków"""
        buildings_data = {
            'residential': 45,
            'commercial': 20,
            'industrial': 15,
            'service': 10
        }
        
        report = BuildingReport(
            total_buildings=90,
            buildings_by_type=buildings_data,
            average_condition=87.5
        )
        
        self.assertEqual(report.total_buildings, 90)
        self.assertEqual(report.buildings_by_type['residential'], 45)
        
    def test_building_efficiency_analysis(self):
        """Test analizy efektywności budynków"""
        buildings_data = {
            'residential': {'count': 45, 'efficiency': 85},
            'commercial': {'count': 20, 'efficiency': 90},
            'industrial': {'count': 15, 'efficiency': 80}
        }
        
        report = BuildingReport(
            total_buildings=80,
            buildings_by_type=buildings_data,
            average_condition=87.5
        )
        
        efficiency = report.calculate_overall_efficiency()
        self.assertGreater(efficiency, 80)
        
    def test_maintenance_schedule(self):
        """Test harmonogramu konserwacji"""
        buildings_needing_maintenance = [
            {'id': 1, 'type': 'residential', 'condition': 65},
            {'id': 2, 'type': 'commercial', 'condition': 70}
        ]
        
        report = BuildingReport(
            total_buildings=100,
            buildings_by_type={'residential': 50, 'commercial': 30},
            buildings_needing_maintenance=buildings_needing_maintenance
        )
        
        schedule = report.generate_maintenance_schedule()
        self.assertEqual(len(schedule), 2)

class TestResourceReport(unittest.TestCase):
    """Testy raportu zasobów"""
    
    def test_resource_report_creation(self):
        """Test tworzenia raportu zasobów"""
        report = ResourceReport(
            power_available=1000,
            power_consumption=850,
            water_available=1200,
            water_consumption=1100
        )
        
        self.assertEqual(report.power_available, 1000)
        self.assertEqual(report.water_available, 1200)
        
    def test_resource_efficiency(self):
        """Test efektywności zasobów"""
        report = ResourceReport(
            power_available=1000,
            power_consumption=850,
            water_available=1200,
            water_consumption=1100
        )
        
        power_efficiency = report.get_power_efficiency()
        water_efficiency = report.get_water_efficiency()
        
        self.assertAlmostEqual(power_efficiency, 85.0)
        self.assertAlmostEqual(water_efficiency, 91.67, places=2)
        
    def test_resource_predictions(self):
        """Test predykcji zużycia zasobów"""
        historical_consumption = [800, 820, 840, 850, 860]
        
        report = ResourceReport(
            power_available=1000,
            power_consumption=850,
            water_available=1200,
            water_consumption=1100
        )
        
        prediction = report.predict_consumption(historical_consumption, 5)
        self.assertGreater(prediction, 850)

class TestPerformanceReport(unittest.TestCase):
    """Testy raportu wydajności"""
    
    def test_performance_report_creation(self):
        """Test tworzenia raportu wydajności"""
        metrics = {
            'fps': 60,
            'memory_usage': 512,
            'cpu_usage': 45,
            'load_time': 2.3
        }
        
        report = PerformanceReport(
            frame_rate=60,
            memory_usage=512,
            cpu_usage=45,
            performance_metrics=metrics
        )
        
        self.assertEqual(report.frame_rate, 60)
        self.assertEqual(report.memory_usage, 512)
        
    def test_performance_analysis(self):
        """Test analizy wydajności"""
        report = PerformanceReport(
            frame_rate=60,
            memory_usage=512,
            cpu_usage=45
        )
        
        performance_score = report.calculate_performance_score()
        self.assertGreater(performance_score, 0)
        self.assertLessEqual(performance_score, 100)
        
    def test_bottleneck_detection(self):
        """Test wykrywania wąskich gardeł"""
        report = PerformanceReport(
            frame_rate=30,  # Niski FPS
            memory_usage=1024,  # Wysokie zużycie pamięci
            cpu_usage=85  # Wysokie zużycie CPU
        )
        
        bottlenecks = report.detect_bottlenecks()
        self.assertGreater(len(bottlenecks), 0)

class TestReportIntegration(unittest.TestCase):
    """Testy integracyjne raportów"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.report_manager = ReportManager()
        self.mock_game_engine = Mock(spec=GameEngine)
        
    def test_generate_comprehensive_report(self):
        """Test generowania kompleksowego raportu"""
        # Mock all necessary data
        self.mock_game_engine.resources.money = 10000
        self.mock_game_engine.population.get_total_population.return_value = 5000
        self.mock_game_engine.get_all_buildings.return_value = []
        
        reports = self.report_manager.generate_comprehensive_report(self.mock_game_engine)
        
        self.assertGreater(len(reports), 0)
        
    def test_report_comparison(self):
        """Test porównywania raportów"""
        report1 = FinancialReport(current_money=10000, total_income=1500, total_expenses=1200)
        report2 = FinancialReport(current_money=11000, total_income=1600, total_expenses=1100)
        
        comparison = self.report_manager.compare_reports(report1, report2)
        
        self.assertIn('money_change', comparison)
        self.assertEqual(comparison['money_change'], 1000)
        
    def test_automated_report_generation(self):
        """Test automatycznego generowania raportów"""
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            
            # Simulate automatic report generation
            result = self.report_manager.setup_automated_reports(
                self.mock_game_engine, 
                interval=3600  # Co godzinę
            )
            
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 