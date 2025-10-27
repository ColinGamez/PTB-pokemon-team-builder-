"""
Team Analytics Dashboard
Real-time team analytics with heatmaps, usage statistics, win-rate tracking,
meta trend analysis, and predictive team building recommendations.
"""

import json
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import pandas as pd
import threading
import time
import math

class AnalyticsTimeframe(Enum):
    """Analytics timeframe options."""
    LAST_24_HOURS = "24h"
    LAST_WEEK = "7d"
    LAST_MONTH = "30d"
    LAST_3_MONTHS = "90d"
    ALL_TIME = "all"

class MetricType(Enum):
    """Types of metrics to track."""
    WIN_RATE = "win_rate"
    USAGE_RATE = "usage_rate"
    DAMAGE_DEALT = "damage_dealt"
    KO_RATE = "ko_rate"
    SURVIVABILITY = "survivability"
    SPEED_TIER = "speed_tier"
    TYPE_COVERAGE = "type_coverage"
    SYNERGY_SCORE = "synergy_score"

class TrendDirection(Enum):
    """Trend direction indicators."""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class PokemonStats:
    """Comprehensive Pokemon statistics."""
    name: str
    total_battles: int
    wins: int
    losses: int
    win_rate: float
    usage_rate: float
    average_damage: float
    kos_scored: int
    times_fainted: int
    survivability_rate: float
    most_used_moves: List[Tuple[str, int]]
    most_effective_items: List[Tuple[str, float]]
    best_teammates: List[Tuple[str, float]]
    worst_matchups: List[Tuple[str, float]]
    trend: TrendDirection
    
@dataclass
class TeamAnalytics:
    """Team performance analytics."""
    team_id: str
    team_name: str
    pokemon_list: List[str]
    total_battles: int
    wins: int
    losses: int
    win_rate: float
    average_battle_length: float
    most_common_lead: str
    synergy_score: float
    type_coverage_score: float
    weakness_coverage: Dict[str, float]
    performance_by_format: Dict[str, Dict[str, Any]]
    monthly_performance: List[Dict[str, Any]]
    recommendation_score: float
    improvements_suggested: List[str]

@dataclass
class MetaAnalysis:
    """Current meta analysis."""
    timeframe: AnalyticsTimeframe
    top_pokemon: List[Tuple[str, float]]  # (name, usage_rate)
    rising_pokemon: List[Tuple[str, float]]  # (name, growth_rate)
    declining_pokemon: List[Tuple[str, float]]  # (name, decline_rate)
    type_distribution: Dict[str, float]
    ability_usage: Dict[str, float]
    item_usage: Dict[str, float]
    move_usage: Dict[str, float]
    team_archetypes: Dict[str, float]
    format_meta: Dict[str, Dict[str, Any]]
    prediction_accuracy: float

@dataclass
class BattleHeatmap:
    """Battle interaction heatmap data."""
    pokemon_matchups: Dict[str, Dict[str, float]]  # win rates between Pokemon
    type_effectiveness_real: Dict[str, Dict[str, float]]  # actual vs theoretical
    move_effectiveness: Dict[str, Dict[str, float]]  # move vs Pokemon matchups
    item_synergy: Dict[str, Dict[str, float]]  # item effectiveness by Pokemon
    ability_impact: Dict[str, Dict[str, float]]  # ability impact by matchup

class AnalyticsDatabase:
    """Database for analytics data storage."""
    
    def __init__(self, db_path: str = "team_analytics.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize analytics database."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Battle records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS battle_records (
                battle_id TEXT PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                format TEXT NOT NULL,
                player1_id TEXT NOT NULL,
                player2_id TEXT NOT NULL,
                winner_id TEXT,
                battle_length INTEGER,
                team1_data TEXT NOT NULL,
                team2_data TEXT NOT NULL,
                battle_log TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Pokemon usage statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_usage_stats (
                pokemon_name TEXT NOT NULL,
                date DATE NOT NULL,
                format TEXT NOT NULL,
                battles_used INTEGER DEFAULT 0,
                battles_won INTEGER DEFAULT 0,
                total_damage REAL DEFAULT 0,
                kos_scored INTEGER DEFAULT 0,
                times_fainted INTEGER DEFAULT 0,
                PRIMARY KEY (pokemon_name, date, format)
            )
        """)
        
        # Team performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_performance (
                team_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                format TEXT NOT NULL,
                battles INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                total_battle_time INTEGER DEFAULT 0,
                team_data TEXT NOT NULL,
                PRIMARY KEY (team_id, date, format)
            )
        """)
        
        # Move usage and effectiveness
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS move_analytics (
                move_name TEXT NOT NULL,
                pokemon_name TEXT NOT NULL,
                date DATE NOT NULL,
                times_used INTEGER DEFAULT 0,
                times_hit INTEGER DEFAULT 0,
                total_damage REAL DEFAULT 0,
                kos_caused INTEGER DEFAULT 0,
                PRIMARY KEY (move_name, pokemon_name, date)
            )
        """)
        
        # Item effectiveness tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_analytics (
                item_name TEXT NOT NULL,
                pokemon_name TEXT NOT NULL,
                date DATE NOT NULL,
                times_used INTEGER DEFAULT 0,
                battles_won INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0,
                PRIMARY KEY (item_name, pokemon_name, date)
            )
        """)
        
        # Meta trends
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta_trends (
                date DATE NOT NULL,
                format TEXT NOT NULL,
                trend_data TEXT NOT NULL,
                analysis_version TEXT DEFAULT '1.0',
                PRIMARY KEY (date, format)
            )
        """)
        
        self.connection.commit()
        
        # Insert sample data for demonstration
        self._insert_sample_data()
    
    def _insert_sample_data(self):
        """Insert sample analytics data."""
        cursor = self.connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM battle_records")
        if cursor.fetchone()[0] > 0:
            return
        
        # Sample battle records
        sample_battles = [
            {
                "battle_id": f"battle_{i:03d}",
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "format": "OU",
                "player1_id": f"player_{i % 10 + 1}",
                "player2_id": f"player_{(i + 5) % 10 + 1}",
                "winner_id": f"player_{i % 2 + 1}",
                "battle_length": 180 + (i * 10) % 300,
                "team1_data": json.dumps({
                    "pokemon": [
                        {"name": "Garchomp", "level": 50},
                        {"name": "Rotom-Wash", "level": 50},
                        {"name": "Ferrothorn", "level": 50}
                    ]
                }),
                "team2_data": json.dumps({
                    "pokemon": [
                        {"name": "Landorus-T", "level": 50},
                        {"name": "Clefable", "level": 50},
                        {"name": "Heatran", "level": 50}
                    ]
                })
            }
            for i in range(100)  # 100 sample battles
        ]
        
        for battle in sample_battles:
            cursor.execute("""
                INSERT OR IGNORE INTO battle_records 
                (battle_id, date, format, player1_id, player2_id, winner_id, 
                 battle_length, team1_data, team2_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                battle["battle_id"], battle["date"], battle["format"],
                battle["player1_id"], battle["player2_id"], battle["winner_id"],
                battle["battle_length"], battle["team1_data"], battle["team2_data"]
            ))
        
        # Sample Pokemon usage stats
        popular_pokemon = [
            "Garchomp", "Landorus-T", "Rotom-Wash", "Ferrothorn", "Clefable",
            "Heatran", "Toxapex", "Corviknight", "Dragapult", "Rillaboom"
        ]
        
        for i, pokemon in enumerate(popular_pokemon):
            for days_ago in range(30):
                date = (datetime.now() - timedelta(days=days_ago)).date()
                cursor.execute("""
                    INSERT OR IGNORE INTO pokemon_usage_stats
                    (pokemon_name, date, format, battles_used, battles_won, 
                     total_damage, kos_scored, times_fainted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pokemon, date, "OU",
                    50 - i * 2 + (days_ago % 10),  # Usage varies
                    25 - i + (days_ago % 5),        # Wins
                    15000 + i * 1000,              # Damage
                    30 + i * 2,                     # KOs
                    15 + i                          # Faints
                ))
        
        self.connection.commit()
    
    def record_battle(self, battle_data: Dict[str, Any]) -> bool:
        """Record a battle for analytics."""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO battle_records 
                (battle_id, date, format, player1_id, player2_id, winner_id,
                 battle_length, team1_data, team2_data, battle_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                battle_data["battle_id"],
                battle_data["date"],
                battle_data["format"],
                battle_data["player1_id"],
                battle_data["player2_id"],
                battle_data.get("winner_id"),
                battle_data.get("battle_length", 0),
                json.dumps(battle_data["team1_data"]),
                json.dumps(battle_data["team2_data"]),
                json.dumps(battle_data.get("battle_log", {}))
            ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error recording battle: {e}")
            return False
    
    def get_pokemon_stats(
        self, 
        pokemon_name: str, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH,
        format_filter: str = "OU"
    ) -> Optional[PokemonStats]:
        """Get comprehensive Pokemon statistics."""
        cursor = self.connection.cursor()
        
        # Calculate date range
        end_date = datetime.now().date()
        if timeframe == AnalyticsTimeframe.LAST_24_HOURS:
            start_date = end_date - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.LAST_WEEK:
            start_date = end_date - timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.LAST_MONTH:
            start_date = end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.LAST_3_MONTHS:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = datetime(2020, 1, 1).date()
        
        # Get Pokemon usage statistics
        cursor.execute("""
            SELECT 
                SUM(battles_used) as total_battles,
                SUM(battles_won) as wins,
                SUM(total_damage) as total_damage,
                SUM(kos_scored) as kos_scored,
                SUM(times_fainted) as times_fainted
            FROM pokemon_usage_stats 
            WHERE pokemon_name = ? AND format = ? 
            AND date BETWEEN ? AND ?
        """, (pokemon_name, format_filter, start_date, end_date))
        
        row = cursor.fetchone()
        if not row or not row["total_battles"]:
            return None
        
        total_battles = row["total_battles"]
        wins = row["wins"] or 0
        total_damage = row["total_damage"] or 0
        kos_scored = row["kos_scored"] or 0
        times_fainted = row["times_fainted"] or 0
        
        losses = total_battles - wins
        win_rate = wins / total_battles if total_battles > 0 else 0
        average_damage = total_damage / total_battles if total_battles > 0 else 0
        survivability_rate = 1 - (times_fainted / total_battles) if total_battles > 0 else 0
        
        # Calculate usage rate (simplified)
        cursor.execute("""
            SELECT SUM(battles_used) as total_format_battles
            FROM pokemon_usage_stats 
            WHERE format = ? AND date BETWEEN ? AND ?
        """, (format_filter, start_date, end_date))
        
        format_total = cursor.fetchone()["total_format_battles"] or 1
        usage_rate = total_battles / format_total
        
        # Get trend direction (simplified)
        trend = self._calculate_pokemon_trend(pokemon_name, format_filter, timeframe)
        
        return PokemonStats(
            name=pokemon_name,
            total_battles=total_battles,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            usage_rate=usage_rate,
            average_damage=average_damage,
            kos_scored=kos_scored,
            times_fainted=times_fainted,
            survivability_rate=survivability_rate,
            most_used_moves=[],  # Would be populated from move_analytics
            most_effective_items=[],  # Would be populated from item_analytics
            best_teammates=[],  # Would be calculated from team data
            worst_matchups=[],  # Would be calculated from battle outcomes
            trend=trend
        )
    
    def _calculate_pokemon_trend(
        self, 
        pokemon_name: str, 
        format_filter: str, 
        timeframe: AnalyticsTimeframe
    ) -> TrendDirection:
        """Calculate Pokemon usage trend."""
        cursor = self.connection.cursor()
        
        # Get recent usage data points
        cursor.execute("""
            SELECT date, battles_used 
            FROM pokemon_usage_stats 
            WHERE pokemon_name = ? AND format = ?
            ORDER BY date DESC
            LIMIT 7
        """, (pokemon_name, format_filter))
        
        rows = cursor.fetchall()
        if len(rows) < 3:
            return TrendDirection.STABLE
        
        usage_values = [row["battles_used"] for row in rows]
        
        # Simple trend calculation
        recent_avg = sum(usage_values[:3]) / 3
        older_avg = sum(usage_values[3:]) / len(usage_values[3:])
        
        change_percent = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        if change_percent > 0.15:
            return TrendDirection.RISING
        elif change_percent < -0.15:
            return TrendDirection.FALLING
        elif abs(change_percent) > 0.3:  # High variance
            return TrendDirection.VOLATILE
        else:
            return TrendDirection.STABLE

class TeamAnalyzer:
    """Advanced team analysis and recommendations."""
    
    def __init__(self, database: AnalyticsDatabase):
        self.database = database
        self.type_chart = self._initialize_type_chart()
    
    def _initialize_type_chart(self) -> Dict[str, Dict[str, float]]:
        """Initialize type effectiveness chart."""
        # Simplified type chart for demo
        return {
            "Fire": {"Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Steel": 2.0, "Water": 0.5, "Fire": 0.5, "Rock": 0.5, "Dragon": 0.5},
            "Water": {"Fire": 2.0, "Ground": 2.0, "Rock": 2.0, "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
            "Grass": {"Water": 2.0, "Ground": 2.0, "Rock": 2.0, "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
            "Electric": {"Water": 2.0, "Flying": 2.0, "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Ground": 0.0},
            # ... (would include full type chart)
        }
    
    def analyze_team(self, team_data: Dict[str, Any], user_id: str) -> TeamAnalytics:
        """Perform comprehensive team analysis."""
        team_pokemon = team_data.get("pokemon", [])
        team_id = team_data.get("team_id", str(time.time()))
        team_name = team_data.get("name", "Unnamed Team")
        
        # Get battle history for this team
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT * FROM team_performance 
            WHERE team_id = ? OR user_id = ?
            ORDER BY date DESC
        """, (team_id, user_id))
        
        performance_rows = cursor.fetchall()
        
        # Calculate basic statistics
        total_battles = sum(row["battles"] for row in performance_rows)
        total_wins = sum(row["wins"] for row in performance_rows)
        total_battle_time = sum(row["total_battle_time"] for row in performance_rows)
        
        win_rate = total_wins / total_battles if total_battles > 0 else 0
        average_battle_length = total_battle_time / total_battles if total_battles > 0 else 0
        
        # Analyze team composition
        synergy_score = self._calculate_synergy_score(team_pokemon)
        type_coverage_score = self._calculate_type_coverage(team_pokemon)
        weakness_coverage = self._analyze_weakness_coverage(team_pokemon)
        
        # Performance by format
        performance_by_format = self._analyze_format_performance(performance_rows)
        
        # Monthly performance trend
        monthly_performance = self._calculate_monthly_performance(performance_rows)
        
        # Generate recommendations
        recommendation_score, improvements = self._generate_team_recommendations(team_pokemon)
        
        # Determine most common lead
        most_common_lead = team_pokemon[0]["name"] if team_pokemon else "Unknown"
        
        return TeamAnalytics(
            team_id=team_id,
            team_name=team_name,
            pokemon_list=[p["name"] for p in team_pokemon],
            total_battles=total_battles,
            wins=total_wins,
            losses=total_battles - total_wins,
            win_rate=win_rate,
            average_battle_length=average_battle_length,
            most_common_lead=most_common_lead,
            synergy_score=synergy_score,
            type_coverage_score=type_coverage_score,
            weakness_coverage=weakness_coverage,
            performance_by_format=performance_by_format,
            monthly_performance=monthly_performance,
            recommendation_score=recommendation_score,
            improvements_suggested=improvements
        )
    
    def _calculate_synergy_score(self, pokemon_list: List[Dict[str, Any]]) -> float:
        """Calculate team synergy score."""
        if len(pokemon_list) < 2:
            return 0.0
        
        synergy_score = 0.0
        
        # Role diversity (simplified)
        roles = []
        for pokemon in pokemon_list:
            stats = pokemon.get("stats", {})
            if not stats:
                continue
            
            # Simple role determination based on stats
            attack = stats.get("attack", 0)
            sp_attack = stats.get("sp_attack", 0)
            defense = stats.get("defense", 0)
            sp_defense = stats.get("sp_defense", 0)
            speed = stats.get("speed", 0)
            
            offensive = max(attack, sp_attack)
            defensive = (defense + sp_defense) / 2
            
            if speed > 100 and offensive > 100:
                roles.append("sweeper")
            elif defensive > 100:
                roles.append("wall")
            elif speed > 80:
                roles.append("pivot")
            else:
                roles.append("balanced")
        
        role_diversity = len(set(roles)) / len(roles) if roles else 0
        synergy_score += role_diversity * 30
        
        # Type synergy
        types = []
        for pokemon in pokemon_list:
            pokemon_types = pokemon.get("types", [])
            types.extend(pokemon_types)
        
        # Check for complementary types
        type_synergy = self._calculate_type_synergy(types)
        synergy_score += type_synergy
        
        return min(100.0, synergy_score)
    
    def _calculate_type_coverage(self, pokemon_list: List[Dict[str, Any]]) -> float:
        """Calculate offensive type coverage."""
        covered_types = set()
        
        for pokemon in pokemon_list:
            moves = pokemon.get("moves", [])
            pokemon_types = pokemon.get("types", [])
            
            # STAB moves
            for ptype in pokemon_types:
                if ptype in self.type_chart:
                    for defending_type, effectiveness in self.type_chart[ptype].items():
                        if effectiveness > 1.0:
                            covered_types.add(defending_type)
            
            # Coverage moves (simplified - would analyze actual moves)
            for move_name in moves:
                # This would look up move types and calculate coverage
                pass
        
        # Score based on how many types are covered
        total_types = 18  # Total Pokemon types
        coverage_score = (len(covered_types) / total_types) * 100
        
        return min(100.0, coverage_score)
    
    def _analyze_weakness_coverage(self, pokemon_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze how well the team covers weaknesses."""
        weakness_coverage = {}
        
        # Get all team weaknesses
        team_weaknesses = defaultdict(int)
        for pokemon in pokemon_list:
            pokemon_types = pokemon.get("types", [])
            for attacking_type in self.type_chart:
                for defending_type in pokemon_types:
                    effectiveness = self.type_chart.get(attacking_type, {}).get(defending_type, 1.0)
                    if effectiveness > 1.0:
                        team_weaknesses[attacking_type] += effectiveness
        
        # Calculate coverage for each weakness
        for weakness_type, weakness_count in team_weaknesses.items():
            # Count how many Pokemon resist this type
            resistances = 0
            for pokemon in pokemon_list:
                pokemon_types = pokemon.get("types", [])
                for defending_type in pokemon_types:
                    effectiveness = self.type_chart.get(weakness_type, {}).get(defending_type, 1.0)
                    if effectiveness < 1.0:
                        resistances += 1
                        break
            
            coverage_ratio = resistances / len(pokemon_list) if pokemon_list else 0
            weakness_coverage[weakness_type] = coverage_ratio
        
        return weakness_coverage
    
    def _calculate_type_synergy(self, types: List[str]) -> float:
        """Calculate type synergy bonus."""
        type_counter = Counter(types)
        
        # Bonus for type diversity
        unique_types = len(type_counter)
        diversity_bonus = min(20, unique_types * 2)
        
        # Bonus for balanced type distribution
        if unique_types > 1:
            type_variance = np.var(list(type_counter.values()))
            balance_bonus = max(0, 10 - type_variance)
        else:
            balance_bonus = 0
        
        return diversity_bonus + balance_bonus
    
    def _analyze_format_performance(self, performance_rows: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by battle format."""
        format_performance = defaultdict(lambda: {"battles": 0, "wins": 0, "win_rate": 0.0})
        
        for row in performance_rows:
            format_name = row["format"]
            format_performance[format_name]["battles"] += row["battles"]
            format_performance[format_name]["wins"] += row["wins"]
        
        # Calculate win rates
        for format_name, stats in format_performance.items():
            if stats["battles"] > 0:
                stats["win_rate"] = stats["wins"] / stats["battles"]
        
        return dict(format_performance)
    
    def _calculate_monthly_performance(self, performance_rows: List[Any]) -> List[Dict[str, Any]]:
        """Calculate monthly performance trends."""
        monthly_data = defaultdict(lambda: {"battles": 0, "wins": 0})
        
        for row in performance_rows:
            try:
                date = datetime.fromisoformat(str(row["date"]))
                month_key = date.strftime("%Y-%m")
                monthly_data[month_key]["battles"] += row["battles"]
                monthly_data[month_key]["wins"] += row["wins"]
            except:
                continue
        
        monthly_performance = []
        for month, stats in monthly_data.items():
            win_rate = stats["wins"] / stats["battles"] if stats["battles"] > 0 else 0
            monthly_performance.append({
                "month": month,
                "battles": stats["battles"],
                "wins": stats["wins"],
                "win_rate": win_rate
            })
        
        return sorted(monthly_performance, key=lambda x: x["month"])
    
    def _generate_team_recommendations(self, pokemon_list: List[Dict[str, Any]]) -> Tuple[float, List[str]]:
        """Generate team improvement recommendations."""
        improvements = []
        recommendation_score = 75.0  # Base score
        
        if len(pokemon_list) < 6:
            improvements.append("Complete your team with more Pokemon")
            recommendation_score -= 15
        
        # Check for speed control
        fast_pokemon = sum(1 for p in pokemon_list 
                          if p.get("stats", {}).get("speed", 0) > 100)
        if fast_pokemon < 2:
            improvements.append("Add more fast Pokemon for speed control")
            recommendation_score -= 10
        
        # Check for defensive presence
        defensive_pokemon = sum(1 for p in pokemon_list
                              if (p.get("stats", {}).get("defense", 0) + 
                                  p.get("stats", {}).get("sp_defense", 0)) > 160)
        if defensive_pokemon < 1:
            improvements.append("Consider adding a defensive wall")
            recommendation_score -= 10
        
        # Check type coverage
        types = []
        for pokemon in pokemon_list:
            types.extend(pokemon.get("types", []))
        
        if len(set(types)) < 8:
            improvements.append("Improve type diversity for better coverage")
            recommendation_score -= 5
        
        return recommendation_score, improvements

class HeatmapGenerator:
    """Generate battle interaction heatmaps."""
    
    def __init__(self, database: AnalyticsDatabase):
        self.database = database
    
    def generate_pokemon_matchup_heatmap(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH
    ) -> BattleHeatmap:
        """Generate Pokemon vs Pokemon matchup heatmap."""
        cursor = self.database.connection.cursor()
        
        # Get battle data
        cursor.execute("""
            SELECT team1_data, team2_data, winner_id, player1_id, player2_id
            FROM battle_records 
            WHERE date >= ?
        """, ((datetime.now() - timedelta(days=30)).isoformat(),))
        
        battles = cursor.fetchall()
        
        # Calculate matchup win rates
        matchup_data = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0}))
        
        for battle in battles:
            try:
                team1 = json.loads(battle["team1_data"])
                team2 = json.loads(battle["team2_data"])
                winner = battle["winner_id"]
                
                team1_pokemon = [p["name"] for p in team1.get("pokemon", [])]
                team2_pokemon = [p["name"] for p in team2.get("pokemon", [])]
                
                # Record matchups
                for p1 in team1_pokemon:
                    for p2 in team2_pokemon:
                        if winner == battle["player1_id"]:
                            matchup_data[p1][p2]["wins"] += 1
                            matchup_data[p2][p1]["losses"] += 1
                        elif winner == battle["player2_id"]:
                            matchup_data[p1][p2]["losses"] += 1
                            matchup_data[p2][p1]["wins"] += 1
            except:
                continue
        
        # Convert to win rate matrix
        pokemon_matchups = {}
        for p1, opponents in matchup_data.items():
            pokemon_matchups[p1] = {}
            for p2, results in opponents.items():
                total = results["wins"] + results["losses"]
                win_rate = results["wins"] / total if total > 0 else 0.5
                pokemon_matchups[p1][p2] = win_rate
        
        return BattleHeatmap(
            pokemon_matchups=pokemon_matchups,
            type_effectiveness_real={},  # Would be calculated
            move_effectiveness={},       # Would be calculated
            item_synergy={},            # Would be calculated
            ability_impact={}           # Would be calculated
        )

class MetaAnalyzer:
    """Analyze current meta trends and predictions."""
    
    def __init__(self, database: AnalyticsDatabase):
        self.database = database
    
    def analyze_current_meta(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH,
        format_filter: str = "OU"
    ) -> MetaAnalysis:
        """Analyze current meta state."""
        cursor = self.database.connection.cursor()
        
        # Calculate date range
        end_date = datetime.now().date()
        if timeframe == AnalyticsTimeframe.LAST_MONTH:
            start_date = end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.LAST_WEEK:
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get top Pokemon by usage
        cursor.execute("""
            SELECT pokemon_name, SUM(battles_used) as total_usage
            FROM pokemon_usage_stats
            WHERE format = ? AND date BETWEEN ? AND ?
            GROUP BY pokemon_name
            ORDER BY total_usage DESC
            LIMIT 20
        """, (format_filter, start_date, end_date))
        
        usage_data = cursor.fetchall()
        total_usage = sum(row["total_usage"] for row in usage_data)
        
        top_pokemon = [(row["pokemon_name"], row["total_usage"] / total_usage) 
                      for row in usage_data]
        
        # Calculate rising/declining Pokemon
        rising_pokemon = self._calculate_rising_pokemon(format_filter, timeframe)
        declining_pokemon = self._calculate_declining_pokemon(format_filter, timeframe)
        
        # Type distribution (simplified)
        type_distribution = self._calculate_type_distribution(usage_data)
        
        return MetaAnalysis(
            timeframe=timeframe,
            top_pokemon=top_pokemon,
            rising_pokemon=rising_pokemon,
            declining_pokemon=declining_pokemon,
            type_distribution=type_distribution,
            ability_usage={},  # Would be calculated from battle data
            item_usage={},     # Would be calculated from battle data
            move_usage={},     # Would be calculated from battle data
            team_archetypes={},# Would be calculated from team data
            format_meta={},    # Would include format-specific analysis
            prediction_accuracy=0.85  # Would be calculated from past predictions
        )
    
    def _calculate_rising_pokemon(
        self, 
        format_filter: str, 
        timeframe: AnalyticsTimeframe
    ) -> List[Tuple[str, float]]:
        """Calculate Pokemon with rising usage."""
        cursor = self.database.connection.cursor()
        
        # Get usage trend over time
        cursor.execute("""
            SELECT pokemon_name, date, SUM(battles_used) as daily_usage
            FROM pokemon_usage_stats
            WHERE format = ?
            GROUP BY pokemon_name, date
            ORDER BY pokemon_name, date DESC
        """, (format_filter,))
        
        usage_trends = defaultdict(list)
        for row in cursor.fetchall():
            usage_trends[row["pokemon_name"]].append(row["daily_usage"])
        
        rising_pokemon = []
        for pokemon, usage_values in usage_trends.items():
            if len(usage_values) >= 7:  # Need at least a week of data
                recent_avg = sum(usage_values[:3]) / 3
                older_avg = sum(usage_values[3:7]) / 4
                
                if older_avg > 0:
                    growth_rate = (recent_avg - older_avg) / older_avg
                    if growth_rate > 0.1:  # 10% growth threshold
                        rising_pokemon.append((pokemon, growth_rate))
        
        return sorted(rising_pokemon, key=lambda x: x[1], reverse=True)[:10]
    
    def _calculate_declining_pokemon(
        self, 
        format_filter: str, 
        timeframe: AnalyticsTimeframe
    ) -> List[Tuple[str, float]]:
        """Calculate Pokemon with declining usage."""
        cursor = self.database.connection.cursor()
        
        # Similar to rising, but looking for negative trends
        cursor.execute("""
            SELECT pokemon_name, date, SUM(battles_used) as daily_usage
            FROM pokemon_usage_stats
            WHERE format = ?
            GROUP BY pokemon_name, date
            ORDER BY pokemon_name, date DESC
        """, (format_filter,))
        
        usage_trends = defaultdict(list)
        for row in cursor.fetchall():
            usage_trends[row["pokemon_name"]].append(row["daily_usage"])
        
        declining_pokemon = []
        for pokemon, usage_values in usage_trends.items():
            if len(usage_values) >= 7:
                recent_avg = sum(usage_values[:3]) / 3
                older_avg = sum(usage_values[3:7]) / 4
                
                if older_avg > 0:
                    decline_rate = (older_avg - recent_avg) / older_avg
                    if decline_rate > 0.1:  # 10% decline threshold
                        declining_pokemon.append((pokemon, decline_rate))
        
        return sorted(declining_pokemon, key=lambda x: x[1], reverse=True)[:10]
    
    def _calculate_type_distribution(self, usage_data: List[Any]) -> Dict[str, float]:
        """Calculate type distribution in the meta."""
        # Simplified type distribution
        # Would map Pokemon names to their types and calculate distribution
        type_distribution = {
            "Steel": 0.15,
            "Fire": 0.12,
            "Water": 0.11,
            "Electric": 0.10,
            "Ground": 0.10,
            "Dragon": 0.09,
            "Flying": 0.08,
            "Grass": 0.07,
            "Fairy": 0.06,
            "Fighting": 0.05,
            "Ghost": 0.04,
            "Psychic": 0.03
        }
        
        return type_distribution

class AnalyticsDashboard:
    """Main analytics dashboard controller."""
    
    def __init__(self):
        self.database = AnalyticsDatabase()
        self.team_analyzer = TeamAnalyzer(self.database)
        self.heatmap_generator = HeatmapGenerator(self.database)
        self.meta_analyzer = MetaAnalyzer(self.database)
        self.update_thread = None
        self.start_background_updates()
    
    def start_background_updates(self):
        """Start background analytics updates."""
        def update_analytics():
            while True:
                try:
                    # Update meta trends daily
                    self._update_meta_trends()
                    time.sleep(86400)  # 24 hours
                except Exception as e:
                    print(f"Analytics update error: {e}")
                    time.sleep(3600)  # Retry in 1 hour
        
        self.update_thread = threading.Thread(target=update_analytics, daemon=True)
        self.update_thread.start()
    
    def _update_meta_trends(self):
        """Update meta trend analysis."""
        current_meta = self.meta_analyzer.analyze_current_meta()
        
        # Store meta trends in database
        cursor = self.database.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO meta_trends (date, format, trend_data)
            VALUES (?, ?, ?)
        """, (
            datetime.now().date(),
            "OU",  # Default format
            json.dumps(asdict(current_meta))
        ))
        
        self.database.connection.commit()
    
    def get_pokemon_analytics(
        self, 
        pokemon_name: str, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH
    ) -> Optional[PokemonStats]:
        """Get comprehensive Pokemon analytics."""
        return self.database.get_pokemon_stats(pokemon_name, timeframe)
    
    def get_team_analytics(self, team_data: Dict[str, Any], user_id: str) -> TeamAnalytics:
        """Get comprehensive team analytics."""
        return self.team_analyzer.analyze_team(team_data, user_id)
    
    def get_meta_analysis(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH
    ) -> MetaAnalysis:
        """Get current meta analysis."""
        return self.meta_analyzer.analyze_current_meta(timeframe)
    
    def get_battle_heatmap(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_MONTH
    ) -> BattleHeatmap:
        """Get battle interaction heatmap."""
        return self.heatmap_generator.generate_pokemon_matchup_heatmap(timeframe)
    
    def generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Get user's recent teams
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT team_data FROM team_performance 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT 5
        """, (user_id,))
        
        recent_teams = cursor.fetchall()
        
        # Analyze each team and generate recommendations
        for team_row in recent_teams:
            try:
                team_data = json.loads(team_row["team_data"])
                analysis = self.team_analyzer.analyze_team(team_data, user_id)
                
                recommendations.append({
                    "type": "team_improvement",
                    "team_name": analysis.team_name,
                    "current_score": analysis.recommendation_score,
                    "improvements": analysis.improvements_suggested,
                    "priority": "high" if analysis.recommendation_score < 60 else "medium"
                })
            except:
                continue
        
        # Add meta-based recommendations
        meta = self.meta_analyzer.analyze_current_meta()
        
        recommendations.append({
            "type": "meta_trends",
            "rising_pokemon": meta.rising_pokemon[:3],
            "declining_pokemon": meta.declining_pokemon[:3],
            "priority": "medium"
        })
        
        return recommendations


# Demo function
def demonstrate_analytics_dashboard():
    """Demonstrate the team analytics dashboard."""
    print("📊 Team Analytics Dashboard Demo")
    print("=" * 60)
    
    # Initialize dashboard
    dashboard = AnalyticsDashboard()
    
    # Get Pokemon analytics
    print("\n🔍 Pokemon Analysis:")
    print("-" * 40)
    pokemon_stats = dashboard.get_pokemon_analytics("Garchomp")
    if pokemon_stats:
        print(f"Pokemon: {pokemon_stats.name}")
        print(f"Win Rate: {pokemon_stats.win_rate:.1%}")
        print(f"Usage Rate: {pokemon_stats.usage_rate:.1%}")
        print(f"Total Battles: {pokemon_stats.total_battles}")
        print(f"Average Damage: {pokemon_stats.average_damage:.0f}")
        print(f"Survivability: {pokemon_stats.survivability_rate:.1%}")
        print(f"Trend: {pokemon_stats.trend.value}")
    
    # Get team analytics
    print("\n🏆 Team Analysis:")
    print("-" * 40)
    sample_team = {
        "team_id": "sample_team_001",
        "name": "OU Balance Team",
        "pokemon": [
            {"name": "Garchomp", "types": ["Dragon", "Ground"], "stats": {"hp": 108, "attack": 130, "defense": 95, "sp_attack": 80, "sp_defense": 85, "speed": 102}},
            {"name": "Rotom-Wash", "types": ["Electric", "Water"], "stats": {"hp": 50, "attack": 65, "defense": 107, "sp_attack": 105, "sp_defense": 107, "speed": 86}},
            {"name": "Ferrothorn", "types": ["Grass", "Steel"], "stats": {"hp": 74, "attack": 94, "defense": 131, "sp_attack": 54, "sp_defense": 116, "speed": 20}}
        ]
    }
    
    team_analytics = dashboard.get_team_analytics(sample_team, "demo_user")
    print(f"Team: {team_analytics.team_name}")
    print(f"Win Rate: {team_analytics.win_rate:.1%}")
    print(f"Total Battles: {team_analytics.total_battles}")
    print(f"Synergy Score: {team_analytics.synergy_score:.1f}/100")
    print(f"Type Coverage: {team_analytics.type_coverage_score:.1f}/100")
    print(f"Recommendation Score: {team_analytics.recommendation_score:.1f}/100")
    
    if team_analytics.improvements_suggested:
        print("Suggested Improvements:")
        for improvement in team_analytics.improvements_suggested:
            print(f"  • {improvement}")
    
    # Get meta analysis
    print("\n📈 Meta Analysis:")
    print("-" * 40)
    meta_analysis = dashboard.get_meta_analysis()
    
    print(f"Top Pokemon ({meta_analysis.timeframe.value}):")
    for i, (pokemon, usage_rate) in enumerate(meta_analysis.top_pokemon[:5], 1):
        print(f"  {i}. {pokemon}: {usage_rate:.1%} usage")
    
    print(f"\nRising Pokemon:")
    for pokemon, growth_rate in meta_analysis.rising_pokemon[:3]:
        print(f"  📈 {pokemon}: +{growth_rate:.1%} growth")
    
    print(f"\nDeclining Pokemon:")
    for pokemon, decline_rate in meta_analysis.declining_pokemon[:3]:
        print(f"  📉 {pokemon}: -{decline_rate:.1%} decline")
    
    # Get recommendations
    print("\n💡 Personalized Recommendations:")
    print("-" * 40)
    recommendations = dashboard.generate_recommendations("demo_user")
    
    for rec in recommendations:
        if rec["type"] == "team_improvement":
            print(f"🏆 Team: {rec['team_name']}")
            print(f"   Score: {rec['current_score']:.1f}/100 | Priority: {rec['priority']}")
            for improvement in rec['improvements']:
                print(f"   • {improvement}")
        elif rec["type"] == "meta_trends":
            print(f"📊 Meta Trends:")
            print(f"   Consider: {', '.join([p[0] for p in rec['rising_pokemon']])}")
    
    print(f"\n🎯 Analytics Dashboard Ready!")
    print("Features: Real-time Statistics, Heatmaps, Meta Trends, Recommendations")

if __name__ == "__main__":
    demonstrate_analytics_dashboard()