# Admin Panel Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     🔒 ADMIN PANEL                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │  Admin Authentication                            │           │
│  │  • PIN: 050270 (6-digit secure PIN)            │           │
│  │  • Session management                           │           │
│  │  • Auto-logout on inactivity                    │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  ┌───────────┬───────────┬───────────┬───────────┬───────────┐│
│  │Dashboard  │  Users    │ Content   │Statistics │ Database  ││
│  │    📊     │    👥     │    📝     │    📈     │    💾     ││
│  └───────────┴───────────┴───────────┴───────────┴───────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 1: DASHBOARD 📊                                      │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │  Total   │  │  Online  │  │  Total   │  │  Email   │ │  │
│  │  │  Users   │  │  Users   │  │  Posts   │  │ Verified │ │  │
│  │  │   150    │  │    25    │  │   483    │  │   120    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  │                                                          │  │
│  │  Recent Activity:                                       │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ ✓ trainer_ash    (Ash Ketchum)                     │ │  │
│  │  │   Joined: 2025-10-26 14:23:15                      │ │  │
│  │  │                                                     │ │  │
│  │  │ ✗ new_user123    (New Trainer)                     │ │  │
│  │  │   Joined: 2025-10-26 14:45:03                      │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  Quick Actions:                                         │  │
│  │  [Refresh Stats] [Export Data] [View Logs]             │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 2: USERS 👥                                          │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │  Search: [________________]  [Search] [Show All]        │  │
│  │                                                          │  │
│  │  User List:                                             │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │Username   │Display   │Email     │Level│Status│...  │ │  │
│  │  ├───────────┼──────────┼──────────┼─────┼──────┼────┤ │  │
│  │  │ash_ketch..│Ash Ket...│ash@pok...│ 15  │online│ ✓  │ │  │
│  │  │misty_wat..│Misty Wa..│misty@p...│ 12  │offli.│ ✓  │ │  │
│  │  │new_user123│New Train.│new@ema...│  1  │offli.│ ✗  │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  Actions:                                               │  │
│  │  [View Details] [Delete User] [Verify Email] [Ban User]│  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 3: CONTENT MODERATION 📝                             │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │  Recent Posts:                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ 📝 My Competitive Team Strategy                    │ │  │
│  │  │    Type: team_share | Posted: 2025-10-26 12:30    │ │  │
│  │  │    [View] [Delete]                                 │ │  │
│  │  ├────────────────────────────────────────────────────┤ │  │
│  │  │ 📝 Tournament Finals Replay                        │ │  │
│  │  │    Type: battle_replay | Posted: 2025-10-26 11:15 │ │  │
│  │  │    [View] [Delete]                                 │ │  │
│  │  ├────────────────────────────────────────────────────┤ │  │
│  │  │ 📝 Looking for Battle Partners                     │ │  │
│  │  │    Type: discussion | Posted: 2025-10-26 09:45    │ │  │
│  │  │    [View] [Delete]                                 │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 4: STATISTICS 📈                                     │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │  USER STATISTICS:                                       │  │
│  │  ────────────────────                                   │  │
│  │  Total Users: 150                                       │  │
│  │  Verified Users: 120                                    │  │
│  │  Online Users: 25                                       │  │
│  │                                                          │  │
│  │  CONTENT STATISTICS:                                    │  │
│  │  ────────────────────                                   │  │
│  │  Total Posts: 483                                       │  │
│  │  Shared Teams: 201                                      │  │
│  │  Battle Replays: 156                                    │  │
│  │                                                          │  │
│  │  SOCIAL STATISTICS:                                     │  │
│  │  ────────────────────                                   │  │
│  │  Total Friendships: 342                                 │  │
│  │  Active Friendships: 315                                │  │
│  │                                                          │  │
│  │  DATABASE STATISTICS:                                   │  │
│  │  ────────────────────                                   │  │
│  │  Database Size: 2,458.32 KB                             │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 5: DATABASE MANAGEMENT 💾                            │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │             Database Management                         │  │
│  │                                                          │  │
│  │              ┌──────────────────────┐                   │  │
│  │              │  Backup Database     │                   │  │
│  │              └──────────────────────┘                   │  │
│  │                                                          │  │
│  │              ┌──────────────────────┐                   │  │
│  │              │ Optimize Database    │                   │  │
│  │              └──────────────────────┘                   │  │
│  │                                                          │  │
│  │              ┌──────────────────────┐                   │  │
│  │              │  Export to JSON      │                   │  │
│  │              └──────────────────────┘                   │  │
│  │                                                          │  │
│  │              ┌──────────────────────┐                   │  │
│  │              │ View Database Schema │                   │  │
│  │              └──────────────────────┘                   │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tab 6: SETTINGS ⚙️                                       │  │
│  │ ─────────────────────────────────────────────────────── │  │
│  │                                                          │  │
│  │         Admin Settings                                  │  │
│  │                                                          │  │
│  │         Change Admin Password:                          │  │
│  │         ┌──────────────────────┐                        │  │
│  │         │  Change Password     │                        │  │
│  │         └──────────────────────┘                        │  │
│  │                                                          │  │
│  │         Email Configuration:                            │  │
│  │         ┌──────────────────────┐                        │  │
│  │         │  Configure SMTP      │                        │  │
│  │         └──────────────────────┘                        │  │
│  │                                                          │  │
│  │         System Maintenance:                             │  │
│  │         ┌──────────────────────┐                        │  │
│  │         │  Clear Old Logs      │                        │  │
│  │         └──────────────────────┘                        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [Logout]                                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
AdminPanelFrame
│
├── AdminLoginDialog
│   ├── Password Entry
│   ├── Authentication Logic
│   └── Session Management
│
├── Dashboard Tab
│   ├── Statistics Cards (4)
│   ├── Recent Activity List
│   └── Quick Actions
│
├── Users Tab
│   ├── Search Bar
│   ├── User TreeView
│   │   ├── Sort by Column
│   │   └── Multi-select Support
│   └── User Actions
│       ├── View Details Dialog
│       ├── Delete Confirmation
│       ├── Email Verification
│       └── Ban User
│
├── Content Moderation Tab
│   ├── Posts Frame
│   ├── Post Items
│   │   ├── Title & Metadata
│   │   └── Action Buttons
│   └── Moderation Actions
│
├── Statistics Tab
│   ├── User Stats
│   ├── Content Stats
│   ├── Social Stats
│   └── Database Stats
│
├── Database Tab
│   ├── Backup Manager
│   ├── Optimization Tools
│   ├── Export Functions
│   └── Schema Viewer
│
└── Settings Tab
    ├── Password Manager
    ├── SMTP Configuration
    └── Maintenance Tools
```

## Data Flow

```
┌──────────────┐
│ Admin Login  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Authentication   │
│ • Check PIN      │
│ • Create Session │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────┐
│ Load Admin Panel         │
│ • Initialize Tabs        │
│ • Connect to Database    │
│ • Load CommunityManager  │
└──────┬───────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ User Interactions                   │
│ ┌─────────────────────────────────┐ │
│ │ View Dashboard                  │ │
│ │   ↓                             │ │
│ │ Query Database (Stats)          │ │
│ │   ↓                             │ │
│ │ Display Statistics              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Manage Users                    │ │
│ │   ↓                             │ │
│ │ Search/Filter (SQL Query)       │ │
│ │   ↓                             │ │
│ │ Display Results (TreeView)      │ │
│ │   ↓                             │ │
│ │ Execute Action (Update/Delete)  │ │
│ │   ↓                             │ │
│ │ Commit Changes (Database)       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Database Operations             │ │
│ │   ↓                             │ │
│ │ Backup/Optimize/Export          │ │
│ │   ↓                             │ │
│ │ File System Operations          │ │
│ │   ↓                             │ │
│ │ Success/Error Message           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Database Schema (Admin-Relevant Tables)

```
users
├── user_id (INTEGER PRIMARY KEY)
├── username (TEXT UNIQUE)
├── email (TEXT)
├── password_hash (TEXT)
├── display_name (TEXT)
├── level (INTEGER)
├── status (TEXT) ─────────► online/offline/banned
├── email_verified (BOOLEAN)
├── verification_token (TEXT)
├── verification_sent_date (TEXT)
└── join_date (TEXT)

community_posts
├── post_id (INTEGER PRIMARY KEY)
├── user_id (INTEGER FK → users)
├── title (TEXT)
├── content (TEXT)
├── post_type (TEXT) ──────► team_share/battle_replay/discussion
├── created_date (TEXT)
└── updated_date (TEXT)

friendships
├── friendship_id (INTEGER PRIMARY KEY)
├── user1_id (INTEGER FK → users)
├── user2_id (INTEGER FK → users)
├── status (TEXT) ─────────► pending/accepted/rejected
└── created_date (TEXT)

team_shares
├── share_id (INTEGER PRIMARY KEY)
├── user_id (INTEGER FK → users)
├── team_data (TEXT JSON)
├── share_date (TEXT)
└── views (INTEGER)

battle_replays
├── replay_id (INTEGER PRIMARY KEY)
├── user_id (INTEGER FK → users)
├── replay_data (TEXT JSON)
├── battle_date (TEXT)
└── views (INTEGER)
```

## Security Layers

```
┌─────────────────────────────────────┐
│ Layer 1: Authentication             │
│ • PIN verification (050270)         │
│ • Session management                │
│ • Auto-logout timeout               │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Layer 2: Authorization              │
│ • Admin role verification           │
│ • Action permission checks          │
│ • Audit logging                     │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Layer 3: Data Protection            │
│ • SQL injection prevention          │
│ • Input validation                  │
│ • Parameterized queries             │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Layer 4: Database Security          │
│ • Transaction rollback              │
│ • Backup before destructive ops     │
│ • Confirmation dialogs              │
└─────────────────────────────────────┘
```

## Future Enhancements Roadmap

```
Phase 1: Enhanced Security
├── SHA-256 PIN hashing
├── Two-factor authentication
├── Session token management
└── IP-based access control

Phase 2: Advanced Features
├── Role-based permissions
│   ├── Super Admin
│   ├── Moderator
│   └── Support Staff
├── Bulk operations
│   ├── Mass email
│   ├── Batch delete
│   └── Bulk verify
└── Advanced analytics
    ├── User engagement graphs
    ├── Growth trends
    └── Content popularity

Phase 3: Automation
├── Auto-moderation rules
├── Scheduled backups
├── Alert notifications
└── Report generation

Phase 4: Integration
├── REST API endpoints
├── Webhook support
├── External tool integration
└── Mobile admin app
```

---

**Created:** October 26, 2025  
**Version:** 1.0  
**Status:** Production Ready
