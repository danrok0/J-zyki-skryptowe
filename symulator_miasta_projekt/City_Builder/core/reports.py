"""
System raportowania i statystyk dla City Builder
Implementuje generowanie wykresów, raportów i eksport danych
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import csv
import os
from dataclasses import dataclass
from enum import Enum
from unittest.mock import Mock

class ReportType(Enum):
    """Typy raportów"""
    FINANCIAL = "financial"
    POPULATION = "population"
    BUILDINGS = "buildings"
    RESOURCES = "resources"
    PERFORMANCE = "performance"
    COMPREHENSIVE = "comprehensive"

class ReportFormat(Enum):
    """Formaty eksportu raportów"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"

@dataclass
class BaseReport:
    """Bazowa klasa dla wszystkich raportów"""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Konwertuje raport do słownika"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'type': self.__class__.__name__
        }

@dataclass
class FinancialReport(BaseReport):
    """Raport finansowy"""
    current_money: float = 0
    total_income: float = 0
    total_expenses: float = 0
    net_income: float = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.net_income is None:
            self.net_income = self.total_income - self.total_expenses
    
    def get_net_income(self) -> float:
        """Oblicza dochód netto"""
        return self.total_income - self.total_expenses
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            'current_money': self.current_money,
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'net_income': self.net_income
        })
        return base_dict
    
    def calculate_trend(self, historical_data: List[Dict]) -> float:
        """Oblicza trend finansowy"""
        if len(historical_data) < 2:
            return 0.0
        
        net_incomes = [data['net_income'] for data in historical_data]
        if len(net_incomes) < 2:
            return 0.0
        
        return (net_incomes[-1] - net_incomes[0]) / max(abs(net_incomes[0]), 1)

@dataclass
class PopulationReport(BaseReport):
    """Raport populacyjny"""
    total_population: int = 0
    satisfaction: float = 50.0
    unemployment_rate: float = 0.0
    growth_rate: float = 0.0
    demographics: Dict = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.demographics is None:
            self.demographics = {}
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            'total_population': self.total_population,
            'satisfaction': self.satisfaction,
            'unemployment_rate': self.unemployment_rate,
            'growth_rate': self.growth_rate,
            'demographics': self.demographics
        })
        return base_dict

@dataclass
class BuildingReport(BaseReport):
    """Raport budynków"""
    buildings_by_type: Dict = None
    total_buildings: int = 0
    average_condition: float = 100.0
    maintenance_needed: List = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.buildings_by_type is None:
            self.buildings_by_type = {}
        if self.maintenance_needed is None:
            self.maintenance_needed = []
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            'buildings_by_type': self.buildings_by_type,
            'total_buildings': self.total_buildings,
            'average_condition': self.average_condition,
            'maintenance_needed': self.maintenance_needed
        })
        return base_dict

@dataclass
class ResourceReport(BaseReport):
    """Raport zasobów"""
    power_available: float = 0
    water_available: float = 0
    power_consumption: float = 0
    water_consumption: float = 0
    efficiency: Dict = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.efficiency is None:
            self.efficiency = {}
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            'power_available': self.power_available,
            'water_available': self.water_available,
            'power_consumption': self.power_consumption,
            'water_consumption': self.water_consumption,
            'efficiency': self.efficiency
        })
        return base_dict

@dataclass
class PerformanceReport(BaseReport):
    """Raport wydajności"""
    fps: float = 60.0
    memory_usage: float = 0.0
    load_times: Dict = None
    bottlenecks: List = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.load_times is None:
            self.load_times = {}
        if self.bottlenecks is None:
            self.bottlenecks = []
    
    def to_dict(self) -> Dict:
        base_dict = super().to_dict()
        base_dict.update({
            'fps': self.fps,
            'memory_usage': self.memory_usage,
            'load_times': self.load_times,
            'bottlenecks': self.bottlenecks
        })
        return base_dict

@dataclass
class ReportData:
    """Dane do raportu"""
    title: str
    data: Dict
    chart_type: str = "line"  # line, bar, pie, scatter
    description: str = ""
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

class ReportManager:
    """Menedżer raportów i statystyk"""
    
    def __init__(self):
        self.historical_data: List[Dict] = []
        self.reports_generated = 0
        self.export_directory = "exports"
        self.reports_history: List[BaseReport] = []
        
        # Utwórz katalog eksportu jeśli nie istnieje
        os.makedirs(self.export_directory, exist_ok=True)
        
        # Konfiguracja matplotlib
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def generate_report(self, report_type: ReportType, game_engine) -> BaseReport:
        """Generuje raport zadanego typu"""
        if report_type == ReportType.FINANCIAL:
            return self._generate_financial_report(game_engine)
        elif report_type == ReportType.POPULATION:
            return self._generate_population_report(game_engine)
        elif report_type == ReportType.BUILDINGS:
            return self._generate_building_report(game_engine)
        elif report_type == ReportType.RESOURCES:
            return self._generate_resource_report(game_engine)
        elif report_type == ReportType.PERFORMANCE:
            return self._generate_performance_report(game_engine)
        else:
            raise ValueError(f"Nieznany typ raportu: {report_type}")
    
    def _generate_financial_report(self, game_engine) -> FinancialReport:
        """Generuje raport finansowy"""
        current_money = getattr(game_engine, 'resources', Mock()).money if hasattr(game_engine, 'resources') else 0
        total_income = game_engine.get_total_income() if hasattr(game_engine, 'get_total_income') else 0
        total_expenses = game_engine.get_total_expenses() if hasattr(game_engine, 'get_total_expenses') else 0
        
        return FinancialReport(
            current_money=current_money,
            total_income=total_income,
            total_expenses=total_expenses
        )
    
    def _generate_population_report(self, game_engine) -> PopulationReport:
        """Generuje raport populacyjny"""
        if hasattr(game_engine, 'population'):
            total_pop = game_engine.population.get_total_population() if hasattr(game_engine.population, 'get_total_population') else 0
            satisfaction = game_engine.population.get_satisfaction() if hasattr(game_engine.population, 'get_satisfaction') else 50
            unemployment = game_engine.population.get_unemployment_rate() if hasattr(game_engine.population, 'get_unemployment_rate') else 0
        else:
            total_pop = 0
            satisfaction = 50
            unemployment = 0
        
        return PopulationReport(
            total_population=total_pop,
            satisfaction=satisfaction,
            unemployment_rate=unemployment
        )
    
    def _generate_building_report(self, game_engine) -> BuildingReport:
        """Generuje raport budynków"""
        buildings = game_engine.get_all_buildings() if hasattr(game_engine, 'get_all_buildings') else []
        
        buildings_by_type = {}
        total_buildings = len(buildings)
        total_condition = 0
        
        for building in buildings:
            building_type = getattr(building, 'building_type', 'unknown')
            condition = getattr(building, 'condition', 100)
            
            if building_type not in buildings_by_type:
                buildings_by_type[building_type] = 0
            buildings_by_type[building_type] += 1
            total_condition += condition
        
        avg_condition = total_condition / max(total_buildings, 1)
        
        return BuildingReport(
            buildings_by_type=buildings_by_type,
            total_buildings=total_buildings,
            average_condition=avg_condition
        )
    
    def _generate_resource_report(self, game_engine) -> ResourceReport:
        """Generuje raport zasobów"""
        if hasattr(game_engine, 'resources'):
            power = getattr(game_engine.resources, 'power', 0)
            water = getattr(game_engine.resources, 'water', 0)
        else:
            power = 0
            water = 0
        
        power_consumption = game_engine.get_power_consumption() if hasattr(game_engine, 'get_power_consumption') else 0
        water_consumption = game_engine.get_water_consumption() if hasattr(game_engine, 'get_water_consumption') else 0
        
        return ResourceReport(
            power_available=power,
            water_available=water,
            power_consumption=power_consumption,
            water_consumption=water_consumption
        )
    
    def _generate_performance_report(self, game_engine) -> PerformanceReport:
        """Generuje raport wydajności"""
        return PerformanceReport()
    
    def save_to_history(self, report: BaseReport):
        """Zapisuje raport do historii"""
        self.reports_history.append(report)
    
    def export_report(self, report: BaseReport, format_type: ReportFormat, filename: str) -> bool:
        """Eksportuje raport do pliku"""
        try:
            if format_type == ReportFormat.JSON:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
            elif format_type == ReportFormat.CSV:
                # Podstawowy eksport CSV
                data = report.to_dict()
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Pole', 'Wartość'])
                    for key, value in data.items():
                        writer.writerow([key, str(value)])
            return True
        except Exception as e:
            print(f"Błąd eksportu: {e}")
            return False

    def record_turn_data(self, turn: int, game_state: Dict):
        """Zapisuje dane z tury do historii"""
        turn_data = {
            'turn': turn,
            'timestamp': datetime.now().isoformat(),
            'population': game_state.get('population', 0),
            'money': game_state.get('money', 0),
            'satisfaction': game_state.get('satisfaction', 50),
            'unemployment_rate': game_state.get('unemployment_rate', 0),
            'crime_rate': game_state.get('crime_rate', 0),
            'pollution_level': game_state.get('pollution_level', 0),
            'energy_consumption': game_state.get('energy_consumption', 0),
            'water_consumption': game_state.get('water_consumption', 0),
            'buildings_count': len(game_state.get('buildings', [])),
            'residential_buildings': len([b for b in game_state.get('buildings', []) if b.get('category') == 'residential']),
            'commercial_buildings': len([b for b in game_state.get('buildings', []) if b.get('category') == 'commercial']),
            'industrial_buildings': len([b for b in game_state.get('buildings', []) if b.get('category') == 'industrial']),
            'public_buildings': len([b for b in game_state.get('buildings', []) if b.get('category') == 'public']),
            'income': game_state.get('income', 0),
            'expenses': game_state.get('expenses', 0),
            'net_income': game_state.get('income', 0) - game_state.get('expenses', 0),
            'tax_rate': game_state.get('tax_rate', 0.1),
            'technologies_researched': len(game_state.get('researched_technologies', [])),
            'active_events': len(game_state.get('active_events', [])),
            'diplomatic_reputation': game_state.get('diplomatic_reputation', 50),
            'active_wars': len(game_state.get('active_wars', [])),
            'active_loans': len(game_state.get('active_loans', [])),
            'total_debt': sum(loan.get('remaining_amount', 0) for loan in game_state.get('active_loans', [])),
            'credit_score': game_state.get('credit_score', 750)
        }
        
        self.historical_data.append(turn_data)
        
        # Zachowaj tylko ostatnie 200 tur
        if len(self.historical_data) > 200:
            self.historical_data.pop(0)
    
    def generate_population_report(self) -> ReportData:
        """Generuje raport demograficzny"""
        if not self.historical_data:
            return ReportData("Raport Demograficzny", {}, description="Brak danych historycznych")
        
        turns = [d['turn'] for d in self.historical_data]
        population = [d['population'] for d in self.historical_data]
        satisfaction = [d['satisfaction'] for d in self.historical_data]
        unemployment = [d['unemployment_rate'] for d in self.historical_data]
        
        # Oblicz trendy
        if len(population) > 1:
            pop_growth = ((population[-1] - population[0]) / max(population[0], 1)) * 100
            avg_satisfaction = sum(satisfaction) / len(satisfaction)
            avg_unemployment = sum(unemployment) / len(unemployment)
        else:
            pop_growth = 0
            avg_satisfaction = satisfaction[0] if satisfaction else 50
            avg_unemployment = unemployment[0] if unemployment else 0
        
        recommendations = []
        if pop_growth < 0:
            recommendations.append("Populacja spada - rozważ obniżenie podatków lub poprawę warunków życia")
        if avg_satisfaction < 50:
            recommendations.append("Niskie zadowolenie - zainwestuj w usługi publiczne i rozrywkę")
        if avg_unemployment > 0.1:
            recommendations.append("Wysokie bezrobocie - zbuduj więcej miejsc pracy")
        
        data = {
            'turns': turns,
            'population': population,
            'satisfaction': satisfaction,
            'unemployment_rate': unemployment,
            'population_growth': pop_growth,
            'avg_satisfaction': avg_satisfaction,
            'avg_unemployment': avg_unemployment,
            'current_population': population[-1] if population else 0
        }
        
        return ReportData(
            "Raport Demograficzny",
            data,
            "line",
            f"Analiza rozwoju populacji miasta. Wzrost populacji: {pop_growth:.1f}%",
            recommendations
        )
    
    def generate_economic_report(self) -> ReportData:
        """Generuje raport ekonomiczny"""
        if not self.historical_data:
            return ReportData("Raport Ekonomiczny", {}, description="Brak danych historycznych")
        
        turns = [d['turn'] for d in self.historical_data]
        money = [d['money'] for d in self.historical_data]
        income = [d['income'] for d in self.historical_data]
        expenses = [d['expenses'] for d in self.historical_data]
        net_income = [d['net_income'] for d in self.historical_data]
        debt = [d['total_debt'] for d in self.historical_data]
        
        # Oblicz wskaźniki ekonomiczne
        if len(money) > 1:
            total_income = sum(income)
            total_expenses = sum(expenses)
            avg_net_income = sum(net_income) / len(net_income)
            current_debt_ratio = debt[-1] / max(money[-1], 1) if money[-1] > 0 else 0
        else:
            total_income = income[0] if income else 0
            total_expenses = expenses[0] if expenses else 0
            avg_net_income = net_income[0] if net_income else 0
            current_debt_ratio = 0
        
        recommendations = []
        if avg_net_income < 0:
            recommendations.append("Ujemny przepływ gotówki - zwiększ dochody lub zmniejsz wydatki")
        if current_debt_ratio > 2:
            recommendations.append("Wysokie zadłużenie - skup się na spłacie pożyczek")
        if money[-1] < 10000:
            recommendations.append("Niski poziom gotówki - zwiększ podatki lub zmniejsz wydatki")
        
        data = {
            'turns': turns,
            'money': money,
            'income': income,
            'expenses': expenses,
            'net_income': net_income,
            'debt': debt,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'avg_net_income': avg_net_income,
            'debt_ratio': current_debt_ratio,
            'budget_balance': total_income - total_expenses
        }
        
        return ReportData(
            "Raport Ekonomiczny",
            data,
            "line",
            f"Analiza sytuacji finansowej miasta. Średni dochód netto: ${avg_net_income:,.0f}",
            recommendations
        )
    
    def create_chart(self, report_data: ReportData, save_path: str = None) -> str:
        """Tworzy wykres na podstawie danych raportu"""
        plt.figure(figsize=(12, 8))
        
        if report_data.chart_type == "line":
            self._create_line_chart(report_data)
        elif report_data.chart_type == "bar":
            self._create_bar_chart(report_data)
        elif report_data.chart_type == "pie":
            self._create_pie_chart(report_data)
        else:
            self._create_line_chart(report_data)  # Domyślnie liniowy
        
        plt.title(report_data.title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            filename = f"{self.export_directory}/{report_data.title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
    
    def _create_line_chart(self, report_data: ReportData):
        """Tworzy wykres liniowy"""
        data = report_data.data
        
        if 'turns' in data:
            turns = data['turns']
            
            # Znajdź wszystkie serie danych do wykreślenia
            series_to_plot = []
            for key, values in data.items():
                if key != 'turns' and isinstance(values, list) and len(values) == len(turns):
                    series_to_plot.append((key, values))
            
            # Wykreśl serie
            for name, values in series_to_plot[:5]:  # Maksymalnie 5 serii
                plt.plot(turns, values, marker='o', label=name.replace('_', ' ').title(), linewidth=2)
            
            plt.xlabel('Tura')
            plt.ylabel('Wartość')
            plt.legend()
            plt.grid(True, alpha=0.3)
    
    def _create_bar_chart(self, report_data: ReportData):
        """Tworzy wykres słupkowy"""
        data = report_data.data
        
        if 'building_distribution' in data:
            distribution = data['building_distribution']
            categories = list(distribution.keys())
            values = list(distribution.values())
            
            bars = plt.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
            plt.xlabel('Typ Budynku')
            plt.ylabel('Liczba Budynków')
            
            # Dodaj wartości na słupkach
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        str(value), ha='center', va='bottom')
        
        plt.xticks(rotation=45)
    
    def _create_pie_chart(self, report_data: ReportData):
        """Tworzy wykres kołowy"""
        data = report_data.data
        
        if 'building_distribution' in data:
            distribution = data['building_distribution']
            labels = list(distribution.keys())
            sizes = list(distribution.values())
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
    
    def export_to_csv(self, report_data: ReportData, filename: str = None) -> str:
        """Eksportuje dane raportu do CSV"""
        if not filename:
            filename = f"{self.export_directory}/{report_data.title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Przygotuj dane do eksportu
        export_data = []
        data = report_data.data
        
        if 'turns' in data:
            turns = data['turns']
            for i, turn in enumerate(turns):
                row = {'Turn': turn}
                for key, values in data.items():
                    if isinstance(values, list) and len(values) == len(turns):
                        row[key.replace('_', ' ').title()] = values[i]
                export_data.append(row)
        else:
            # Jeśli brak danych czasowych, eksportuj jako pojedynczy wiersz
            row = {}
            for key, value in data.items():
                if not isinstance(value, (list, dict)):
                    row[key.replace('_', ' ').title()] = value
            export_data.append(row)
        
        # Zapisz do CSV
        if export_data:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = export_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)
        
        return filename
    
    def generate_comprehensive_report(self) -> Dict:
        """Generuje kompleksowy raport ze wszystkich obszarów"""
        reports = {
            'population': self.generate_population_report(),
            'economic': self.generate_economic_report()
        }
        
        # Generuj wykresy
        chart_files = {}
        for report_name, report_data in reports.items():
            chart_files[report_name] = self.create_chart(report_data)
        
        # Oblicz ogólną ocenę miasta
        overall_score = self._calculate_overall_score(reports)
        
        self.reports_generated += 1
        
        return {
            'reports': reports,
            'chart_files': chart_files,
            'overall_score': overall_score,
            'generation_time': datetime.now().isoformat(),
            'report_number': self.reports_generated
        }
    
    def _calculate_overall_score(self, reports: Dict) -> Dict:
        """Oblicza ogólną ocenę miasta na podstawie wszystkich raportów"""
        scores = {}
        
        # Populacja (0-100)
        pop_data = reports['population'].data
        if 'avg_satisfaction' in pop_data:
            scores['population'] = min(100, max(0, pop_data['avg_satisfaction']))
        
        # Ekonomia (0-100)
        econ_data = reports['economic'].data
        if 'avg_net_income' in econ_data:
            scores['economy'] = min(100, max(0, 50 + econ_data['avg_net_income'] / 1000))
        
        # Ogólna ocena
        if scores:
            overall = sum(scores.values()) / len(scores)
            grade = 'A' if overall >= 80 else 'B' if overall >= 60 else 'C' if overall >= 40 else 'D'
        else:
            overall = 0
            grade = 'F'
        
        return {
            'category_scores': scores,
            'overall_score': overall,
            'grade': grade,
            'description': self._get_score_description(overall)
        }
    
    def _get_score_description(self, score: float) -> str:
        """Zwraca opis oceny miasta"""
        if score >= 90:
            return "Doskonale zarządzane miasto - wzór do naśladowania"
        elif score >= 80:
            return "Bardzo dobrze rozwijające się miasto"
        elif score >= 70:
            return "Dobrze zarządzane miasto z potencjałem rozwoju"
        elif score >= 60:
            return "Miasto o średnim poziomie rozwoju"
        elif score >= 50:
            return "Miasto wymagające poprawy w kilku obszarach"
        elif score >= 40:
            return "Miasto z poważnymi problemami do rozwiązania"
        else:
            return "Miasto w kryzysie - wymagane natychmiastowe działania"
    
    def save_to_dict(self) -> Dict:
        """Zapisuje stan do słownika"""
        return {
            'historical_data': self.historical_data[-50:],  # Ostatnie 50 rekordów
            'reports_generated': self.reports_generated
        }
    
    def load_from_dict(self, data: Dict):
        """Wczytuje stan ze słownika"""
        self.historical_data = data.get('historical_data', [])
        self.reports_generated = data.get('reports_generated', 0) 