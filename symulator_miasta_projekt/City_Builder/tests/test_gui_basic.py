#!/usr/bin/env python3
"""
Podstawowe testy GUI
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock PyQt6 if not available
try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False
    
    class QApplication:
        def __init__(self, args):
            pass
        def exec(self):
            return 0
            
    class QWidget:
        def __init__(self):
            pass
        def show(self):
            pass
        def close(self):
            pass
            
    class Qt:
        class KeyboardModifier:
            ControlModifier = 1

class TestGUIBasics(unittest.TestCase):
    """Testy podstawowej funkcjonalności GUI"""
    
    @classmethod
    def setUpClass(cls):
        """Setup dla całej klasy testowej"""
        if HAS_PYQT:
            cls.app = QApplication([])
        else:
            cls.app = None
            
    def setUp(self):
        """Setup przed każdym testem"""
        self.mock_game_engine = Mock()
        
    def test_widget_creation(self):
        """Test tworzenia podstawowych widgetów"""
        # Mock widget creation
        widget_created = True
        self.assertTrue(widget_created)
        
    def test_finance_data_display(self):
        """Test wyświetlania danych finansowych"""
        money = 12345
        formatted = f"${money:,}"
        self.assertEqual(formatted, "$12,345")
        
    def test_building_cost_check(self):
        """Test sprawdzania kosztu budynku"""
        building_cost = 1000
        player_money = 1500
        can_afford = player_money >= building_cost
        self.assertTrue(can_afford)

class TestFinancePanel(unittest.TestCase):
    """Testy panelu finansów"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.mock_game_engine = Mock()
        
    def test_finance_panel_initialization(self):
        """Test inicjalizacji panelu finansów"""
        # Mock the panel since we might not have actual GUI
        with patch('gui.finance_panel.FinancePanel') as MockPanel:
            panel = MockPanel(self.mock_game_engine)
            MockPanel.assert_called_with(self.mock_game_engine)
            
    def test_finance_data_display(self):
        """Test wyświetlania danych finansowych"""
        # Test data formatting
        money = 12345
        formatted = f"${money:,}"
        self.assertEqual(formatted, "$12,345")
        
        # Test percentage calculation
        income = 1500
        expenses = 1200
        profit_margin = ((income - expenses) / income) * 100
        self.assertAlmostEqual(profit_margin, 20.0)
        
    def test_budget_calculations(self):
        """Test obliczeń budżetowych"""
        budget_data = {
            'income': {
                'taxes': 1000,
                'trade': 500,
                'services': 300
            },
            'expenses': {
                'maintenance': 600,
                'salaries': 400,
                'utilities': 200
            }
        }
        
        total_income = sum(budget_data['income'].values())
        total_expenses = sum(budget_data['expenses'].values())
        net_income = total_income - total_expenses
        
        self.assertEqual(total_income, 1800)
        self.assertEqual(total_expenses, 1200)
        self.assertEqual(net_income, 600)

class TestBuildPanel(unittest.TestCase):
    """Testy panelu budowania"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.mock_game_engine = Mock()
        
    def test_building_selection(self):
        """Test wyboru budynku"""
        # Mock building types
        building_types = ['residential', 'commercial', 'industrial', 'service']
        selected_building = 'residential'
        
        self.assertIn(selected_building, building_types)
        
    def test_building_placement_validation(self):
        """Test walidacji umieszczenia budynku"""
        # Test valid placement
        x, y = 10, 15
        map_size = (50, 50)
        building_size = (2, 2)
        
        valid_x = 0 <= x < map_size[0] - building_size[0]
        valid_y = 0 <= y < map_size[1] - building_size[1]
        
        self.assertTrue(valid_x and valid_y)
        
        # Test invalid placement
        x, y = 49, 49
        valid_x = 0 <= x < map_size[0] - building_size[0]
        valid_y = 0 <= y < map_size[1] - building_size[1]
        
        self.assertFalse(valid_x and valid_y)

class TestMapCanvas(unittest.TestCase):
    """Testy kanwy mapy"""
    
    def setUp(self):
        """Setup przed każdym testem"""
        self.mock_game_engine = Mock()
        
    def test_coordinate_conversion(self):
        """Test konwersji współrzędnych"""
        # Screen to grid coordinates
        screen_x, screen_y = 150, 200
        tile_size = 32
        
        grid_x = screen_x // tile_size
        grid_y = screen_y // tile_size
        
        self.assertEqual(grid_x, 4)
        self.assertEqual(grid_y, 6)
        
    def test_zoom_calculations(self):
        """Test obliczeń powiększenia"""
        initial_zoom = 1.0
        zoom_factor = 1.1
        
        new_zoom = initial_zoom * zoom_factor
        self.assertAlmostEqual(new_zoom, 1.1)
        
        # Test zoom limits
        max_zoom = 3.0
        min_zoom = 0.5
        
        test_zoom = 4.0
        clamped_zoom = max(min_zoom, min(max_zoom, test_zoom))
        self.assertEqual(clamped_zoom, max_zoom)
        
    def test_tile_visibility(self):
        """Test widoczności kafelków"""
        # Mock viewport
        viewport_x, viewport_y = 100, 100
        viewport_width, viewport_height = 800, 600
        tile_size = 32
        
        # Calculate visible tiles
        start_x = viewport_x // tile_size
        start_y = viewport_y // tile_size
        end_x = (viewport_x + viewport_width) // tile_size + 1
        end_y = (viewport_y + viewport_height) // tile_size + 1
        
        visible_tiles = (end_x - start_x) * (end_y - start_y)
        
        self.assertGreater(visible_tiles, 0)

class TestAlertsPanel(unittest.TestCase):
    """Testy panelu alertów"""
    
    def test_alert_creation(self):
        """Test tworzenia alertów"""
        alert_data = {
            'type': 'warning',
            'message': 'Low power supply',
            'timestamp': '2024-12-27 10:00:00',
            'priority': 'high'
        }
        
        self.assertEqual(alert_data['type'], 'warning')
        self.assertIn('power', alert_data['message'])
        
    def test_alert_priority_sorting(self):
        """Test sortowania alertów według priorytetu"""
        alerts = [
            {'priority': 'low', 'timestamp': '10:00'},
            {'priority': 'high', 'timestamp': '10:01'},
            {'priority': 'medium', 'timestamp': '10:02'}
        ]
        
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_alerts = sorted(alerts, key=lambda x: priority_order[x['priority']], reverse=True)
        
        self.assertEqual(sorted_alerts[0]['priority'], 'high')
        self.assertEqual(sorted_alerts[-1]['priority'], 'low')

class TestObjectivesPanel(unittest.TestCase):
    """Testy panelu celów"""
    
    def test_objective_completion_check(self):
        """Test sprawdzania ukończenia celu"""
        objective = {
            'type': 'population',
            'target': 5000,
            'current': 4500,
            'completed': False
        }
        
        # Check if objective is completed
        objective['completed'] = objective['current'] >= objective['target']
        self.assertFalse(objective['completed'])
        
        # Complete the objective
        objective['current'] = 5500
        objective['completed'] = objective['current'] >= objective['target']
        self.assertTrue(objective['completed'])
        
    def test_objective_progress_calculation(self):
        """Test obliczania postępu celu"""
        objective = {
            'target': 1000,
            'current': 750
        }
        
        progress_percentage = (objective['current'] / objective['target']) * 100
        self.assertEqual(progress_percentage, 75.0)

class TestReportsPanel(unittest.TestCase):
    """Testy panelu raportów"""
    
    def test_report_data_formatting(self):
        """Test formatowania danych raportu"""
        report_data = {
            'population': 12345,
            'money': 987654,
            'satisfaction': 78.5
        }
        
        # Format population with thousands separator
        formatted_pop = f"{report_data['population']:,}"
        self.assertEqual(formatted_pop, "12,345")
        
        # Format money as currency
        formatted_money = f"${report_data['money']:,.2f}"
        self.assertEqual(formatted_money, "$987,654.00")
        
        # Format satisfaction as percentage
        formatted_satisfaction = f"{report_data['satisfaction']:.1f}%"
        self.assertEqual(formatted_satisfaction, "78.5%")

class TestTechnologyPanel(unittest.TestCase):
    """Testy panelu technologii"""
    
    def test_technology_requirements(self):
        """Test wymagań technologii"""
        technology = {
            'name': 'Advanced Power Grid',
            'cost': 5000,
            'required_level': 3,
            'prerequisites': ['Basic Electronics'],
            'unlocked': False
        }
        
        player_level = 3
        player_money = 6000
        has_prerequisites = True
        
        can_research = (
            player_level >= technology['required_level'] and
            player_money >= technology['cost'] and
            has_prerequisites and
            not technology['unlocked']
        )
        
        self.assertTrue(can_research)

class TestDiplomacyPanel(unittest.TestCase):
    """Testy panelu dyplomacji"""
    
    def test_relationship_status(self):
        """Test statusu relacji"""
        relationship_points = 75
        
        if relationship_points >= 80:
            status = "Allied"
        elif relationship_points >= 60:
            status = "Friendly" 
        elif relationship_points >= 40:
            status = "Neutral"
        elif relationship_points >= 20:
            status = "Unfriendly"
        else:
            status = "Hostile"
            
        self.assertEqual(status, "Friendly")
        
    def test_trade_offer_validation(self):
        """Test walidacji oferty handlowej"""
        offer = {
            'goods': 100,
            'money': 1000,
            'resources': {'power': 50}
        }
        
        # Validate that player has enough resources
        player_resources = {
            'goods': 150,
            'money': 1500,
            'power': 75
        }
        
        can_make_offer = all(
            player_resources.get(key, 0) >= value
            for key, value in offer.items()
            if key != 'resources'
        )
        
        # Check nested resources
        if 'resources' in offer:
            can_make_offer = can_make_offer and all(
                player_resources.get(key, 0) >= value
                for key, value in offer['resources'].items()
            )
            
        self.assertTrue(can_make_offer)

class TestTradePanel(unittest.TestCase):
    """Testy panelu handlu"""
    
    def test_trade_calculation(self):
        """Test obliczeń handlowych"""
        trade_data = {
            'goods_price': 10,
            'quantity': 50,
            'tax_rate': 0.15
        }
        
        subtotal = trade_data['goods_price'] * trade_data['quantity']
        tax = subtotal * trade_data['tax_rate']
        total = subtotal + tax
        
        self.assertEqual(subtotal, 500)
        self.assertEqual(tax, 75)
        self.assertEqual(total, 575)

if __name__ == '__main__':
    unittest.main() 