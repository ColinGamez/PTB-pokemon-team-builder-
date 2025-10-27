# Pokemon Team Builder - Web Interface

## Overview

The Pokemon Team Builder Web Interface provides browser-based access to all Pokemon Team Builder features. Built with Flask and modern web technologies, it offers a responsive, interactive experience for team building, tournaments, and competitive Pokemon management.

## Features

### 🌐 **Web-Based Interface**
- Responsive design that works on desktop, tablet, and mobile
- Modern Bootstrap 5 UI with custom Pokemon-themed styling
- Real-time updates using WebSocket connections
- Progressive Web App (PWA) capabilities

### 👥 **User Management**
- Simple username-based authentication
- User profiles with statistics and ratings
- Session management and persistent login
- User dashboard with personalized content

### 🔧 **Team Building Tools**
- Interactive Pokemon search and selection
- Drag-and-drop team composition
- Real-time stat calculations and analysis
- Team import/export functionality
- Save and load multiple teams

### 📊 **Analytics & Optimization**
- Team analysis with type coverage visualization
- Weakness and strength identification
- Move effectiveness calculations
- Competitive viability scoring

### 🏆 **Tournament System**
- Create and join tournaments
- Real-time bracket updates
- Multiple tournament formats
- Live match tracking and results

### ⚔️ **Battle System**
- Browser-based battle simulator
- Real-time battle mechanics
- Damage calculations and predictions
- Battle replay system

### 🥚 **Breeding Calculator**
- Web-based IV inheritance calculator
- Nature planning and optimization
- Egg group compatibility checking
- Breeding path recommendations

## Technical Architecture

### Backend (Flask)
- **Flask 2.3.3**: Core web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **Flask-CORS**: Cross-origin resource sharing
- **RESTful API**: JSON-based API endpoints
- **Session Management**: Secure user sessions

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Socket.IO**: Real-time client communication
- **Vanilla JavaScript**: Modern ES6+ features
- **Custom CSS**: Pokemon-themed styling
- **Progressive Enhancement**: Works with or without JavaScript

### Real-Time Features
- Live tournament bracket updates
- Real-time battle synchronization
- Instant team collaboration
- Push notifications for events

## Installation & Setup

### Prerequisites
```bash
# Install Python dependencies
pip install Flask Flask-CORS Flask-SocketIO python-socketio eventlet

# Or install from requirements
pip install -r web/requirements.txt
```

### Quick Start
```bash
# Launch the web server
python launch_web.py

# Or run directly
cd web
python app.py
```

### Configuration
Environment variables for customization:
- `FLASK_HOST`: Server host (default: 0.0.0.0)
- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: False)

## API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout

### Teams
- `GET /api/teams` - List user teams
- `POST /api/teams` - Create new team
- `GET /api/teams/<id>` - Get team details
- `PUT /api/teams/<id>` - Update team
- `DELETE /api/teams/<id>` - Delete team
- `GET /api/teams/<id>/analyze` - Analyze team

### Pokemon
- `GET /api/pokemon/search` - Search Pokemon database

### Tournaments
- `GET /api/tournaments` - List tournaments
- `POST /api/tournaments` - Create tournament
- `POST /api/tournaments/<id>/join` - Join tournament

### Breeding
- `POST /api/breeding/calculate` - Calculate breeding outcomes

## WebSocket Events

### Client → Server
- `join_room` - Join real-time room
- `leave_room` - Leave real-time room
- `battle_move` - Submit battle move
- `tournament_update` - Tournament action

### Server → Client
- `connected` - Connection established
- `battle_update` - Battle state change
- `tournament_updated` - Tournament bracket update
- `notification` - System notification

## File Structure

```
web/
├── app.py                 # Main Flask application
├── requirements.txt       # Web-specific dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Custom styling
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── images/           # Static images
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── login.html        # Login page
    └── dashboard.html    # User dashboard
```

## Features by Page

### 🏠 **Homepage** (`/`)
- Feature overview and statistics
- User registration/login
- Latest updates and news
- Quick start guide

### 📊 **Dashboard** (`/dashboard`)
- User statistics and ratings
- Team management overview
- Recent battle history
- Quick action buttons

### 🔧 **Team Builder** (`/team-builder`)
- Interactive Pokemon selection
- Team composition interface
- Real-time stat calculations
- Save/load team functionality

### 🏆 **Tournaments** (`/tournaments`)
- Active tournament listing
- Tournament creation interface
- Bracket visualization
- Join/leave tournament actions

### ⚔️ **Battle** (`/battle`)
- Battle room creation/joining
- Real-time battle interface
- Move selection and execution
- Battle history and replays

### 🥚 **Breeding** (`/breeding`)
- Parent Pokemon selection
- IV inheritance calculator
- Nature planning tools
- Breeding optimization

## Security Features

- Session-based authentication
- CSRF protection on forms
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure cookie configuration

## Performance Optimizations

- Gzip compression for static files
- Browser caching headers
- Minified CSS and JavaScript
- Efficient database queries
- WebSocket connection pooling

## Browser Compatibility

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+
- **Features**: ES6+, WebSocket, localStorage, CSS Grid/Flexbox

## Deployment Options

### Development
```bash
python launch_web.py
# Runs on http://localhost:5000
```

### Production
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -k eventlet web.app:app

# Using Docker
docker build -t pokemon-team-builder-web .
docker run -p 5000:5000 pokemon-team-builder-web
```

## Contributing

The web interface integrates seamlessly with the core Pokemon Team Builder modules:
- `core/`: Pokemon data and mechanics
- `teambuilder/`: Team management logic
- `battle/`: Battle simulation engine
- `features/`: Advanced features (breeding, tournaments)

## Future Enhancements

- **Progressive Web App**: Offline functionality and app installation
- **Database Integration**: Persistent data storage with PostgreSQL/MySQL
- **User Authentication**: OAuth integration (Google, Discord, Twitter)
- **Real-time Collaboration**: Shared team building sessions
- **Mobile Optimization**: Touch-friendly interface improvements
- **Tournament Streaming**: Live tournament broadcasting
- **Social Features**: Friend systems and team sharing

## License

Part of the Pokemon Team Builder project. See main project README for license information.

---

**Ready to battle online!** 🌐⚔️

The web interface brings Pokemon Team Builder to browsers everywhere, making competitive team building accessible to trainers around the world.