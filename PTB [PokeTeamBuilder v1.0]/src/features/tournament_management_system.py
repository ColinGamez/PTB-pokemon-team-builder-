"""
Advanced Tournament Management System
Complete tournament system with bracket generation, live streaming,
spectator mode, prize pools, and automated tournament management.
"""

import json
import sqlite3
import time
import uuid
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import math
import random

class TournamentType(Enum):
    """Tournament format types."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS_SYSTEM = "swiss_system"
    LADDER = "ladder"

class TournamentStatus(Enum):
    """Tournament status states."""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchStatus(Enum):
    """Individual match status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    FORFEIT = "forfeit"
    NO_SHOW = "no_show"

class PrizeType(Enum):
    """Prize pool types."""
    CASH = "cash"
    POINTS = "points"
    ITEMS = "items"
    BADGES = "badges"
    TITLES = "titles"

@dataclass
class TournamentSettings:
    """Tournament configuration settings."""
    format: str  # "OU", "VGC", "Little Cup", etc.
    team_preview: bool
    timer_enabled: bool
    time_per_turn: int  # seconds
    time_per_game: int  # seconds
    best_of: int  # 1, 3, 5, etc.
    sleep_clause: bool
    species_clause: bool
    item_clause: bool
    evasion_clause: bool
    moody_clause: bool
    ohko_clause: bool
    endless_battle_clause: bool
    
@dataclass
class Prize:
    """Tournament prize information."""
    position: int  # 1st, 2nd, 3rd, etc.
    prize_type: PrizeType
    amount: float
    description: str
    currency: str = "USD"

@dataclass
class Participant:
    """Tournament participant."""
    user_id: str
    username: str
    display_name: str
    skill_rating: int
    team_sheet: Optional[Dict[str, Any]]
    registration_time: datetime
    seed: int
    checked_in: bool
    disqualified: bool
    notes: str

@dataclass
class Match:
    """Tournament match."""
    match_id: str
    tournament_id: str
    round_number: int
    match_number: int
    player1_id: Optional[str]
    player2_id: Optional[str]
    winner_id: Optional[str]
    status: MatchStatus
    scheduled_time: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    game_results: List[Dict[str, Any]]
    stream_url: Optional[str]
    spectator_count: int
    replay_data: Optional[Dict[str, Any]]
    notes: str

@dataclass
class Tournament:
    """Complete tournament structure."""
    tournament_id: str
    name: str
    description: str
    organizer_id: str
    tournament_type: TournamentType
    status: TournamentStatus
    settings: TournamentSettings
    
    # Registration
    max_participants: int
    registration_start: datetime
    registration_end: datetime
    entry_fee: float
    
    # Schedule
    start_time: datetime
    estimated_end_time: datetime
    
    # Participants
    participants: List[Participant]
    bracket: Dict[str, Any]
    matches: List[Match]
    
    # Prizes
    prize_pool: List[Prize]
    total_prize_value: float
    
    # Streaming
    stream_enabled: bool
    main_stream_url: Optional[str]
    spectator_limit: int
    
    # Stats
    view_count: int
    created_time: datetime
    updated_time: datetime

class BracketGenerator:
    """Generate tournament brackets for different formats."""
    
    @staticmethod
    def generate_single_elimination(participants: List[Participant]) -> Dict[str, Any]:
        """Generate single elimination bracket."""
        num_participants = len(participants)
        
        # Calculate number of rounds needed
        num_rounds = math.ceil(math.log2(num_participants))
        bracket_size = 2 ** num_rounds
        
        # Seed participants
        seeded_participants = sorted(participants, key=lambda p: p.seed)
        
        # Create bracket structure
        bracket = {
            "type": "single_elimination",
            "rounds": num_rounds,
            "bracket_size": bracket_size,
            "matches": []
        }
        
        # Generate first round matches
        matches = []
        match_number = 1
        
        for i in range(0, bracket_size, 2):
            player1 = seeded_participants[i] if i < num_participants else None
            player2 = seeded_participants[i + 1] if i + 1 < num_participants else None
            
            # Handle byes
            if player2 is None and player1 is not None:
                # Player 1 gets a bye
                match = {
                    "match_id": str(uuid.uuid4()),
                    "round": 1,
                    "match_number": match_number,
                    "player1_id": player1.user_id,
                    "player2_id": None,
                    "winner_id": player1.user_id,
                    "status": "completed",
                    "is_bye": True
                }
            else:
                match = {
                    "match_id": str(uuid.uuid4()),
                    "round": 1,
                    "match_number": match_number,
                    "player1_id": player1.user_id if player1 else None,
                    "player2_id": player2.user_id if player2 else None,
                    "winner_id": None,
                    "status": "pending",
                    "is_bye": False
                }
            
            matches.append(match)
            match_number += 1
        
        bracket["matches"] = matches
        
        # Generate subsequent round placeholders
        for round_num in range(2, num_rounds + 1):
            prev_round_matches = len([m for m in matches if m["round"] == round_num - 1])
            current_round_matches = prev_round_matches // 2
            
            for i in range(current_round_matches):
                match = {
                    "match_id": str(uuid.uuid4()),
                    "round": round_num,
                    "match_number": i + 1,
                    "player1_id": None,
                    "player2_id": None,
                    "winner_id": None,
                    "status": "pending",
                    "is_bye": False,
                    "depends_on": []  # Will be filled with parent match IDs
                }
                matches.append(match)
        
        return bracket
    
    @staticmethod
    def generate_double_elimination(participants: List[Participant]) -> Dict[str, Any]:
        """Generate double elimination bracket."""
        num_participants = len(participants)
        
        # Double elimination requires winners and losers brackets
        bracket = {
            "type": "double_elimination",
            "winners_bracket": BracketGenerator.generate_single_elimination(participants),
            "losers_bracket": {
                "rounds": [],
                "matches": []
            },
            "grand_final": {
                "match_id": str(uuid.uuid4()),
                "requires_reset": True  # Winner must beat loser twice if from losers bracket
            }
        }
        
        return bracket
    
    @staticmethod
    def generate_round_robin(participants: List[Participant]) -> Dict[str, Any]:
        """Generate round robin bracket."""
        num_participants = len(participants)
        matches = []
        match_number = 1
        
        # Every participant plays every other participant once
        for i in range(num_participants):
            for j in range(i + 1, num_participants):
                match = {
                    "match_id": str(uuid.uuid4()),
                    "round": 1,  # All matches are in round 1 for round robin
                    "match_number": match_number,
                    "player1_id": participants[i].user_id,
                    "player2_id": participants[j].user_id,
                    "winner_id": None,
                    "status": "pending"
                }
                matches.append(match)
                match_number += 1
        
        bracket = {
            "type": "round_robin",
            "total_matches": len(matches),
            "matches": matches,
            "standings": {p.user_id: {"wins": 0, "losses": 0, "draws": 0} for p in participants}
        }
        
        return bracket
    
    @staticmethod
    def generate_swiss_system(participants: List[Participant], rounds: int = None) -> Dict[str, Any]:
        """Generate Swiss system bracket."""
        num_participants = len(participants)
        
        # Default to log2(participants) rounds
        if rounds is None:
            rounds = max(3, math.ceil(math.log2(num_participants)))
        
        bracket = {
            "type": "swiss_system",
            "total_rounds": rounds,
            "current_round": 1,
            "matches": [],
            "standings": {
                p.user_id: {
                    "points": 0,
                    "opponents": [],
                    "colors": [],  # For chess-like games
                    "tiebreak_scores": []
                } for p in participants
            }
        }
        
        # Generate first round pairings (random or by rating)
        shuffled_participants = participants.copy()
        random.shuffle(shuffled_participants)
        
        matches = []
        for i in range(0, num_participants - 1, 2):
            if i + 1 < num_participants:
                match = {
                    "match_id": str(uuid.uuid4()),
                    "round": 1,
                    "match_number": (i // 2) + 1,
                    "player1_id": shuffled_participants[i].user_id,
                    "player2_id": shuffled_participants[i + 1].user_id,
                    "winner_id": None,
                    "status": "pending"
                }
                matches.append(match)
        
        bracket["matches"] = matches
        return bracket

class StreamingManager:
    """Manage tournament streaming and spectator features."""
    
    def __init__(self):
        self.active_streams = {}
        self.spectator_counts = defaultdict(int)
        self.stream_callbacks = []
        self.chat_messages = defaultdict(list)
    
    def create_stream(
        self, 
        tournament_id: str, 
        match_id: str,
        stream_key: str = None
    ) -> Dict[str, Any]:
        """Create a new stream for a match."""
        
        stream_id = str(uuid.uuid4())
        stream_key = stream_key or f"stream_{stream_id}"
        
        stream_info = {
            "stream_id": stream_id,
            "tournament_id": tournament_id,
            "match_id": match_id,
            "stream_key": stream_key,
            "stream_url": f"https://stream.example.com/{stream_key}",
            "embed_url": f"https://stream.example.com/embed/{stream_key}",
            "chat_enabled": True,
            "created_time": datetime.now(),
            "spectator_count": 0,
            "peak_viewers": 0,
            "status": "active"
        }
        
        self.active_streams[stream_id] = stream_info
        return stream_info
    
    def join_stream(self, stream_id: str, user_id: str) -> bool:
        """Add spectator to stream."""
        if stream_id in self.active_streams:
            self.spectator_counts[stream_id] += 1
            self.active_streams[stream_id]["spectator_count"] = self.spectator_counts[stream_id]
            
            # Update peak viewers
            current_count = self.spectator_counts[stream_id]
            if current_count > self.active_streams[stream_id]["peak_viewers"]:
                self.active_streams[stream_id]["peak_viewers"] = current_count
            
            return True
        return False
    
    def leave_stream(self, stream_id: str, user_id: str) -> bool:
        """Remove spectator from stream."""
        if stream_id in self.active_streams and self.spectator_counts[stream_id] > 0:
            self.spectator_counts[stream_id] -= 1
            self.active_streams[stream_id]["spectator_count"] = self.spectator_counts[stream_id]
            return True
        return False
    
    def send_chat_message(
        self, 
        stream_id: str, 
        user_id: str, 
        username: str, 
        message: str
    ) -> bool:
        """Send chat message to stream."""
        if stream_id in self.active_streams:
            chat_message = {
                "message_id": str(uuid.uuid4()),
                "user_id": user_id,
                "username": username,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "is_moderator": False,  # Could be determined from user permissions
                "is_subscriber": False
            }
            
            self.chat_messages[stream_id].append(chat_message)
            
            # Keep only last 100 messages
            if len(self.chat_messages[stream_id]) > 100:
                self.chat_messages[stream_id] = self.chat_messages[stream_id][-100:]
            
            # Notify stream callbacks
            for callback in self.stream_callbacks:
                try:
                    callback("chat_message", {
                        "stream_id": stream_id,
                        "message": chat_message
                    })
                except Exception as e:
                    print(f"Stream callback error: {e}")
            
            return True
        return False
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information."""
        return self.active_streams.get(stream_id)
    
    def get_chat_messages(self, stream_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat messages."""
        messages = self.chat_messages.get(stream_id, [])
        return messages[-limit:]

class TournamentDatabase:
    """Database management for tournaments."""
    
    def __init__(self, db_path: str = "tournaments.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize tournament database."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Tournaments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                organizer_id TEXT NOT NULL,
                tournament_type TEXT NOT NULL,
                status TEXT NOT NULL,
                settings TEXT NOT NULL,
                max_participants INTEGER NOT NULL,
                registration_start TIMESTAMP NOT NULL,
                registration_end TIMESTAMP NOT NULL,
                entry_fee REAL DEFAULT 0,
                start_time TIMESTAMP NOT NULL,
                estimated_end_time TIMESTAMP,
                bracket TEXT,
                prize_pool TEXT,
                total_prize_value REAL DEFAULT 0,
                stream_enabled BOOLEAN DEFAULT FALSE,
                main_stream_url TEXT,
                spectator_limit INTEGER DEFAULT 1000,
                view_count INTEGER DEFAULT 0,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Participants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournament_participants (
                tournament_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT NOT NULL,
                skill_rating INTEGER DEFAULT 1000,
                team_sheet TEXT,
                registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seed INTEGER,
                checked_in BOOLEAN DEFAULT FALSE,
                disqualified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                PRIMARY KEY (tournament_id, user_id),
                FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id)
            )
        """)
        
        # Matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournament_matches (
                match_id TEXT PRIMARY KEY,
                tournament_id TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                match_number INTEGER NOT NULL,
                player1_id TEXT,
                player2_id TEXT,
                winner_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                scheduled_time TIMESTAMP,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                game_results TEXT,
                stream_url TEXT,
                spectator_count INTEGER DEFAULT 0,
                replay_data TEXT,
                notes TEXT,
                FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id)
            )
        """)
        
        self.connection.commit()
    
    def create_tournament(self, tournament: Tournament) -> bool:
        """Create a new tournament."""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tournaments (
                    tournament_id, name, description, organizer_id, tournament_type,
                    status, settings, max_participants, registration_start, registration_end,
                    entry_fee, start_time, estimated_end_time, bracket, prize_pool,
                    total_prize_value, stream_enabled, main_stream_url, spectator_limit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tournament.tournament_id, tournament.name, tournament.description,
                tournament.organizer_id, tournament.tournament_type.value,
                tournament.status.value, json.dumps(asdict(tournament.settings)),
                tournament.max_participants, tournament.registration_start.isoformat(),
                tournament.registration_end.isoformat(), tournament.entry_fee,
                tournament.start_time.isoformat(),
                tournament.estimated_end_time.isoformat() if tournament.estimated_end_time else None,
                json.dumps(tournament.bracket), json.dumps([asdict(p) for p in tournament.prize_pool]),
                tournament.total_prize_value, tournament.stream_enabled,
                tournament.main_stream_url, tournament.spectator_limit
            ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating tournament: {e}")
            return False
    
    def register_participant(self, tournament_id: str, participant: Participant) -> bool:
        """Register a participant for a tournament."""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tournament_participants (
                    tournament_id, user_id, username, display_name, skill_rating,
                    team_sheet, seed, checked_in, disqualified, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tournament_id, participant.user_id, participant.username,
                participant.display_name, participant.skill_rating,
                json.dumps(participant.team_sheet) if participant.team_sheet else None,
                participant.seed, participant.checked_in, participant.disqualified,
                participant.notes
            ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error registering participant: {e}")
            return False
    
    def get_tournament(self, tournament_id: str) -> Optional[Tournament]:
        """Get tournament by ID."""
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT * FROM tournaments WHERE tournament_id = ?", (tournament_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get participants
        cursor.execute("""
            SELECT * FROM tournament_participants WHERE tournament_id = ?
        """, (tournament_id,))
        
        participant_rows = cursor.fetchall()
        participants = []
        
        for p_row in participant_rows:
            participant = Participant(
                user_id=p_row["user_id"],
                username=p_row["username"],
                display_name=p_row["display_name"],
                skill_rating=p_row["skill_rating"],
                team_sheet=json.loads(p_row["team_sheet"]) if p_row["team_sheet"] else None,
                registration_time=datetime.fromisoformat(p_row["registration_time"]),
                seed=p_row["seed"],
                checked_in=bool(p_row["checked_in"]),
                disqualified=bool(p_row["disqualified"]),
                notes=p_row["notes"] or ""
            )
            participants.append(participant)
        
        # Get matches
        cursor.execute("""
            SELECT * FROM tournament_matches WHERE tournament_id = ?
            ORDER BY round_number, match_number
        """, (tournament_id,))
        
        match_rows = cursor.fetchall()
        matches = []
        
        for m_row in match_rows:
            match = Match(
                match_id=m_row["match_id"],
                tournament_id=m_row["tournament_id"],
                round_number=m_row["round_number"],
                match_number=m_row["match_number"],
                player1_id=m_row["player1_id"],
                player2_id=m_row["player2_id"],
                winner_id=m_row["winner_id"],
                status=MatchStatus(m_row["status"]),
                scheduled_time=datetime.fromisoformat(m_row["scheduled_time"]) if m_row["scheduled_time"] else None,
                start_time=datetime.fromisoformat(m_row["start_time"]) if m_row["start_time"] else None,
                end_time=datetime.fromisoformat(m_row["end_time"]) if m_row["end_time"] else None,
                game_results=json.loads(m_row["game_results"]) if m_row["game_results"] else [],
                stream_url=m_row["stream_url"],
                spectator_count=m_row["spectator_count"],
                replay_data=json.loads(m_row["replay_data"]) if m_row["replay_data"] else None,
                notes=m_row["notes"] or ""
            )
            matches.append(match)
        
        # Construct tournament object
        tournament = Tournament(
            tournament_id=row["tournament_id"],
            name=row["name"],
            description=row["description"] or "",
            organizer_id=row["organizer_id"],
            tournament_type=TournamentType(row["tournament_type"]),
            status=TournamentStatus(row["status"]),
            settings=TournamentSettings(**json.loads(row["settings"])),
            max_participants=row["max_participants"],
            registration_start=datetime.fromisoformat(row["registration_start"]),
            registration_end=datetime.fromisoformat(row["registration_end"]),
            entry_fee=row["entry_fee"],
            start_time=datetime.fromisoformat(row["start_time"]),
            estimated_end_time=datetime.fromisoformat(row["estimated_end_time"]) if row["estimated_end_time"] else None,
            participants=participants,
            bracket=json.loads(row["bracket"]) if row["bracket"] else {},
            matches=matches,
            prize_pool=[Prize(**p) for p in json.loads(row["prize_pool"])] if row["prize_pool"] else [],
            total_prize_value=row["total_prize_value"],
            stream_enabled=bool(row["stream_enabled"]),
            main_stream_url=row["main_stream_url"],
            spectator_limit=row["spectator_limit"],
            view_count=row["view_count"],
            created_time=datetime.fromisoformat(row["created_time"]),
            updated_time=datetime.fromisoformat(row["updated_time"])
        )
        
        return tournament

class TournamentManager:
    """Main tournament management system."""
    
    def __init__(self):
        self.database = TournamentDatabase()
        self.streaming_manager = StreamingManager()
        self.bracket_generator = BracketGenerator()
        self.active_tournaments = {}
        self.event_callbacks = []
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background processing tasks."""
        # Tournament status updates
        threading.Timer(60.0, self._update_tournament_statuses).start()
        
        # Match scheduling
        threading.Timer(30.0, self._process_match_scheduling).start()
    
    def _update_tournament_statuses(self):
        """Update tournament statuses automatically."""
        current_time = datetime.now()
        
        # This would iterate through active tournaments and update statuses
        # For demo purposes, we'll implement basic logic
        
        # Schedule next update
        threading.Timer(60.0, self._update_tournament_statuses).start()
    
    def _process_match_scheduling(self):
        """Process automatic match scheduling."""
        # This would handle automatic match scheduling and notifications
        
        # Schedule next processing
        threading.Timer(30.0, self._process_match_scheduling).start()
    
    def create_tournament(
        self,
        name: str,
        organizer_id: str,
        tournament_type: TournamentType,
        settings: TournamentSettings,
        max_participants: int,
        registration_start: datetime,
        registration_end: datetime,
        start_time: datetime,
        entry_fee: float = 0.0,
        prize_pool: List[Prize] = None,
        stream_enabled: bool = False
    ) -> str:
        """Create a new tournament."""
        
        tournament_id = str(uuid.uuid4())
        prize_pool = prize_pool or []
        
        # Calculate estimated end time based on tournament type and participants
        estimated_duration = self._estimate_tournament_duration(tournament_type, max_participants)
        estimated_end_time = start_time + estimated_duration
        
        tournament = Tournament(
            tournament_id=tournament_id,
            name=name,
            description="",
            organizer_id=organizer_id,
            tournament_type=tournament_type,
            status=TournamentStatus.DRAFT,
            settings=settings,
            max_participants=max_participants,
            registration_start=registration_start,
            registration_end=registration_end,
            entry_fee=entry_fee,
            start_time=start_time,
            estimated_end_time=estimated_end_time,
            participants=[],
            bracket={},
            matches=[],
            prize_pool=prize_pool,
            total_prize_value=sum(prize.amount for prize in prize_pool),
            stream_enabled=stream_enabled,
            main_stream_url=None,
            spectator_limit=1000,
            view_count=0,
            created_time=datetime.now(),
            updated_time=datetime.now()
        )
        
        if self.database.create_tournament(tournament):
            self.active_tournaments[tournament_id] = tournament
            return tournament_id
        
        return ""
    
    def _estimate_tournament_duration(self, tournament_type: TournamentType, max_participants: int) -> timedelta:
        """Estimate tournament duration."""
        base_minutes = 30  # Base time per match
        
        if tournament_type == TournamentType.SINGLE_ELIMINATION:
            num_rounds = math.ceil(math.log2(max_participants))
            total_matches = max_participants - 1
            estimated_minutes = total_matches * (base_minutes / num_rounds)  # Parallel matches
        elif tournament_type == TournamentType.DOUBLE_ELIMINATION:
            estimated_minutes = max_participants * base_minutes * 1.5  # 50% longer
        elif tournament_type == TournamentType.ROUND_ROBIN:
            total_matches = (max_participants * (max_participants - 1)) / 2
            estimated_minutes = total_matches * base_minutes / 4  # Assume 4 parallel matches
        else:
            estimated_minutes = max_participants * base_minutes
        
        return timedelta(minutes=int(estimated_minutes))
    
    def register_participant(
        self,
        tournament_id: str,
        user_id: str,
        username: str,
        display_name: str,
        skill_rating: int = 1000,
        team_sheet: Dict[str, Any] = None
    ) -> bool:
        """Register a participant for a tournament."""
        
        tournament = self.database.get_tournament(tournament_id)
        if not tournament:
            return False
        
        # Check registration is open
        current_time = datetime.now()
        if current_time < tournament.registration_start or current_time > tournament.registration_end:
            return False
        
        # Check if tournament is full
        if len(tournament.participants) >= tournament.max_participants:
            return False
        
        # Check if already registered
        if any(p.user_id == user_id for p in tournament.participants):
            return False
        
        participant = Participant(
            user_id=user_id,
            username=username,
            display_name=display_name,
            skill_rating=skill_rating,
            team_sheet=team_sheet,
            registration_time=datetime.now(),
            seed=len(tournament.participants) + 1,  # Temporary seed
            checked_in=False,
            disqualified=False,
            notes=""
        )
        
        return self.database.register_participant(tournament_id, participant)
    
    def start_tournament(self, tournament_id: str) -> bool:
        """Start a tournament and generate brackets."""
        tournament = self.database.get_tournament(tournament_id)
        if not tournament:
            return False
        
        # Check minimum participants
        if len(tournament.participants) < 2:
            return False
        
        # Generate bracket based on tournament type
        if tournament.tournament_type == TournamentType.SINGLE_ELIMINATION:
            bracket = self.bracket_generator.generate_single_elimination(tournament.participants)
        elif tournament.tournament_type == TournamentType.DOUBLE_ELIMINATION:
            bracket = self.bracket_generator.generate_double_elimination(tournament.participants)
        elif tournament.tournament_type == TournamentType.ROUND_ROBIN:
            bracket = self.bracket_generator.generate_round_robin(tournament.participants)
        elif tournament.tournament_type == TournamentType.SWISS_SYSTEM:
            bracket = self.bracket_generator.generate_swiss_system(tournament.participants)
        else:
            return False
        
        # Create matches in database
        for match_data in bracket.get("matches", []):
            match = Match(
                match_id=match_data["match_id"],
                tournament_id=tournament_id,
                round_number=match_data["round"],
                match_number=match_data["match_number"],
                player1_id=match_data["player1_id"],
                player2_id=match_data["player2_id"],
                winner_id=match_data.get("winner_id"),
                status=MatchStatus(match_data.get("status", "pending")),
                scheduled_time=None,
                start_time=None,
                end_time=None,
                game_results=[],
                stream_url=None,
                spectator_count=0,
                replay_data=None,
                notes=""
            )
            
            # Save match to database
            cursor = self.database.connection.cursor()
            cursor.execute("""
                INSERT INTO tournament_matches (
                    match_id, tournament_id, round_number, match_number,
                    player1_id, player2_id, winner_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match.match_id, match.tournament_id, match.round_number,
                match.match_number, match.player1_id, match.player2_id,
                match.winner_id, match.status.value
            ))
        
        # Update tournament status
        cursor = self.database.connection.cursor()
        cursor.execute("""
            UPDATE tournaments SET status = ?, bracket = ?, updated_time = CURRENT_TIMESTAMP
            WHERE tournament_id = ?
        """, (TournamentStatus.IN_PROGRESS.value, json.dumps(bracket), tournament_id))
        
        self.database.connection.commit()
        
        # Trigger event callbacks
        self._trigger_event("tournament_started", {"tournament_id": tournament_id})
        
        return True
    
    def report_match_result(
        self,
        match_id: str,
        winner_id: str,
        game_results: List[Dict[str, Any]] = None
    ) -> bool:
        """Report the result of a match."""
        cursor = self.database.connection.cursor()
        
        game_results = game_results or []
        
        cursor.execute("""
            UPDATE tournament_matches 
            SET winner_id = ?, status = ?, end_time = CURRENT_TIMESTAMP,
                game_results = ?
            WHERE match_id = ?
        """, (winner_id, MatchStatus.COMPLETED.value, json.dumps(game_results), match_id))
        
        if cursor.rowcount > 0:
            self.database.connection.commit()
            
            # Advance bracket and schedule next matches
            self._advance_bracket(match_id)
            
            # Trigger event callbacks
            self._trigger_event("match_completed", {
                "match_id": match_id,
                "winner_id": winner_id,
                "game_results": game_results
            })
            
            return True
        
        return False
    
    def _advance_bracket(self, completed_match_id: str):
        """Advance bracket after match completion."""
        # This would implement the logic to advance winners to next rounds
        # and handle tournament progression
        pass
    
    def create_match_stream(self, match_id: str) -> Optional[str]:
        """Create a stream for a specific match."""
        cursor = self.database.connection.cursor()
        cursor.execute("""
            SELECT tournament_id FROM tournament_matches WHERE match_id = ?
        """, (match_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        tournament_id = row["tournament_id"]
        stream_info = self.streaming_manager.create_stream(tournament_id, match_id)
        
        # Update match with stream URL
        cursor.execute("""
            UPDATE tournament_matches SET stream_url = ? WHERE match_id = ?
        """, (stream_info["stream_url"], match_id))
        
        self.database.connection.commit()
        
        return stream_info["stream_id"]
    
    def get_tournament_standings(self, tournament_id: str) -> List[Dict[str, Any]]:
        """Get current tournament standings."""
        tournament = self.database.get_tournament(tournament_id)
        if not tournament:
            return []
        
        standings = []
        
        if tournament.tournament_type == TournamentType.ROUND_ROBIN:
            # Calculate wins/losses for each participant
            participant_stats = {p.user_id: {"wins": 0, "losses": 0, "draws": 0} for p in tournament.participants}
            
            for match in tournament.matches:
                if match.status == MatchStatus.COMPLETED and match.winner_id:
                    if match.winner_id == match.player1_id:
                        participant_stats[match.player1_id]["wins"] += 1
                        if match.player2_id:
                            participant_stats[match.player2_id]["losses"] += 1
                    elif match.winner_id == match.player2_id:
                        participant_stats[match.player2_id]["wins"] += 1
                        if match.player1_id:
                            participant_stats[match.player1_id]["losses"] += 1
            
            # Create standings
            for participant in tournament.participants:
                stats = participant_stats[participant.user_id]
                standings.append({
                    "user_id": participant.user_id,
                    "username": participant.username,
                    "display_name": participant.display_name,
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "draws": stats["draws"],
                    "points": stats["wins"] * 3 + stats["draws"],  # 3 points for win, 1 for draw
                    "status": "active" if not participant.disqualified else "disqualified"
                })
            
            # Sort by points descending
            standings.sort(key=lambda x: x["points"], reverse=True)
            
            # Add rankings
            for i, standing in enumerate(standings):
                standing["rank"] = i + 1
        
        return standings
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger event callbacks."""
        for callback in self.event_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def add_event_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add event callback function."""
        self.event_callbacks.append(callback)
    
    def get_tournament_statistics(self, tournament_id: str) -> Dict[str, Any]:
        """Get comprehensive tournament statistics."""
        tournament = self.database.get_tournament(tournament_id)
        if not tournament:
            return {}
        
        stats = {
            "tournament_info": {
                "name": tournament.name,
                "type": tournament.tournament_type.value,
                "status": tournament.status.value,
                "participants": len(tournament.participants),
                "max_participants": tournament.max_participants,
                "entry_fee": tournament.entry_fee,
                "total_prize_pool": tournament.total_prize_value
            },
            "match_statistics": {
                "total_matches": len(tournament.matches),
                "completed_matches": len([m for m in tournament.matches if m.status == MatchStatus.COMPLETED]),
                "pending_matches": len([m for m in tournament.matches if m.status == MatchStatus.PENDING]),
                "in_progress_matches": len([m for m in tournament.matches if m.status == MatchStatus.IN_PROGRESS])
            },
            "streaming_statistics": {
                "stream_enabled": tournament.stream_enabled,
                "peak_viewers": max([m.spectator_count for m in tournament.matches], default=0),
                "total_views": tournament.view_count
            },
            "timeline": {
                "registration_start": tournament.registration_start.isoformat(),
                "registration_end": tournament.registration_end.isoformat(),
                "tournament_start": tournament.start_time.isoformat(),
                "estimated_end": tournament.estimated_end_time.isoformat() if tournament.estimated_end_time else None
            }
        }
        
        return stats


# Demo and example usage
def demonstrate_tournament_system():
    """Demonstrate the advanced tournament management system."""
    print("🏆 Advanced Tournament Management System Demo")
    print("=" * 70)
    
    # Initialize tournament manager
    tournament_manager = TournamentManager()
    
    # Create tournament settings
    settings = TournamentSettings(
        format="OU",
        team_preview=True,
        timer_enabled=True,
        time_per_turn=30,
        time_per_game=1800,
        best_of=3,
        sleep_clause=True,
        species_clause=True,
        item_clause=True,
        evasion_clause=True,
        moody_clause=True,
        ohko_clause=True,
        endless_battle_clause=True
    )
    
    # Create prize pool
    prize_pool = [
        Prize(1, PrizeType.CASH, 500.0, "First Place", "USD"),
        Prize(2, PrizeType.CASH, 250.0, "Second Place", "USD"),
        Prize(3, PrizeType.CASH, 100.0, "Third Place", "USD"),
        Prize(4, PrizeType.BADGES, 1.0, "Participant Badge", "")
    ]
    
    # Create tournament
    tournament_id = tournament_manager.create_tournament(
        name="Pokemon Masters Championship 2025",
        organizer_id="organizer_001",
        tournament_type=TournamentType.SINGLE_ELIMINATION,
        settings=settings,
        max_participants=16,
        registration_start=datetime.now(),
        registration_end=datetime.now() + timedelta(days=1),
        start_time=datetime.now() + timedelta(days=2),
        entry_fee=25.0,
        prize_pool=prize_pool,
        stream_enabled=True
    )
    
    print(f"✅ Created Tournament: {tournament_id}")
    
    # Register participants
    participants = [
        ("user_001", "ChampionAsh", "Ash Ketchum", 1850),
        ("user_002", "DragonMaster", "Lance", 1820),
        ("user_003", "PsychicMaster", "Sabrina", 1790),
        ("user_004", "RockSolid", "Brock", 1750),
        ("user_005", "WaterExpert", "Misty", 1780),
        ("user_006", "FireBlaze", "Blaine", 1760),
        ("user_007", "GrassGuru", "Erika", 1740),
        ("user_008", "ElectricShock", "Lt. Surge", 1770)
    ]
    
    registered_count = 0
    for user_id, username, display_name, rating in participants:
        if tournament_manager.register_participant(
            tournament_id, user_id, username, display_name, rating
        ):
            registered_count += 1
    
    print(f"✅ Registered {registered_count} participants")
    
    # Start tournament
    if tournament_manager.start_tournament(tournament_id):
        print("✅ Tournament started successfully!")
        
        # Get tournament details
        tournament = tournament_manager.database.get_tournament(tournament_id)
        if tournament:
            print(f"\n📊 Tournament Details:")
            print(f"  Name: {tournament.name}")
            print(f"  Type: {tournament.tournament_type.value}")
            print(f"  Status: {tournament.status.value}")
            print(f"  Participants: {len(tournament.participants)}")
            print(f"  Matches: {len(tournament.matches)}")
            print(f"  Prize Pool: ${tournament.total_prize_value}")
            
            print(f"\n🏅 Bracket Preview:")
            bracket = tournament.bracket
            if bracket and "matches" in bracket:
                round_1_matches = [m for m in bracket["matches"] if m["round"] == 1]
                for i, match in enumerate(round_1_matches[:4], 1):  # Show first 4 matches
                    p1 = next((p for p in tournament.participants if p.user_id == match["player1_id"]), None)
                    p2 = next((p for p in tournament.participants if p.user_id == match["player2_id"]), None)
                    
                    p1_name = p1.display_name if p1 else "BYE"
                    p2_name = p2.display_name if p2 else "BYE"
                    
                    print(f"  Match {match['match_number']}: {p1_name} vs {p2_name}")
            
            # Create a stream for the first match
            if tournament.matches:
                first_match = tournament.matches[0]
                stream_id = tournament_manager.create_match_stream(first_match.match_id)
                if stream_id:
                    print(f"\n📺 Stream created for Match 1: {stream_id}")
    
    # Get tournament statistics
    stats = tournament_manager.get_tournament_statistics(tournament_id)
    if stats:
        print(f"\n📈 Tournament Statistics:")
        info = stats["tournament_info"]
        match_stats = stats["match_statistics"]
        
        print(f"  Tournament: {info['name']}")
        print(f"  Format: {info['type']} | Status: {info['status']}")
        print(f"  Participants: {info['participants']}/{info['max_participants']}")
        print(f"  Entry Fee: ${info['entry_fee']} | Prize Pool: ${info['total_prize_pool']}")
        print(f"  Matches - Total: {match_stats['total_matches']}, Completed: {match_stats['completed_matches']}")
    
    print(f"\n🎮 Tournament Management System Ready!")
    print("Features: Bracket Generation, Live Streaming, Spectator Mode, Prize Pools")

if __name__ == "__main__":
    from collections import defaultdict  # Add missing import
    demonstrate_tournament_system()