# Social Community Hub - User Guide

## Overview
The Pokemon Team Builder Social Community Hub is a comprehensive social networking system that allows trainers to connect, share teams, compete in tournaments, and engage with the Pokemon community.

## Key Features

### 🔐 User Authentication
- **Secure Registration**: Create an account with username, email, and password
- **Username Validation**: Usernames must be unique and follow specific rules:
  - 3-20 characters long
  - Only letters, numbers, and underscores allowed
  - Case-insensitive uniqueness (e.g., "Ash_Ketchum" and "ash_ketchum" cannot both exist)
- **Email Verification**: Receive verification emails to protect your account
- **Password Security**: Passwords are hashed using SHA-256 encryption

### 📧 Email Verification System

#### How It Works
1. **Register**: Create your account with a valid email address
2. **Receive Email**: A verification link is sent to your email
3. **Verify**: Click the link to verify your email address
4. **Access Features**: Some features require email verification

#### Demo Mode
In demo/development mode, verification links are saved to:
```
logs/email_verifications.txt
```

You can find your verification link in this file and use it to verify your account.

#### Production Mode
To enable real email sending, configure SMTP settings:

1. Set environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

2. For Gmail, create an App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App Passwords
   - Generate a new app password for "Mail"

### 👤 User Profiles
- **Custom Display Names**: Choose how you appear to others
- **Bio**: Write about yourself and your Pokemon journey
- **Level & Experience**: Earn XP through community participation
- **Badges & Achievements**: Unlock rewards for accomplishments
- **Avatar**: Customize your profile picture (coming soon)

### 👥 Friends System
- **Send Friend Requests**: Connect with other trainers
- **Accept/Decline**: Manage incoming friend requests
- **Online Status**: See when friends are online, away, busy, or offline
- **Friend Profiles**: View detailed information about your friends

### 📋 Team Sharing
- **Share Teams**: Upload your competitive teams with the community
- **Team Ratings**: Rate teams and provide feedback
- **Tags & Formats**: Categorize teams by format (OU, UU, etc.)
- **Download Teams**: Import popular teams into your own collection
- **Featured Teams**: Browse editor-selected featured teams

### 🎬 Battle Replays
- **Save Battles**: Record your battles for later review
- **Share Replays**: Let others learn from your strategies
- **Replay Theater**: Watch replays with full battle data
- **Statistics**: View turn count, duration, and battle outcomes

### 🏆 Tournaments
- **Create Tournaments**: Host your own community events
- **Join Tournaments**: Compete against other trainers
- **Bracket System**: Automatic bracket generation
- **Tournament Formats**: Support for various competitive formats
- **Prizes & Rankings**: Earn rewards and climb the leaderboards

### 💬 Community Posts
- **Discussion Posts**: Start conversations with the community
- **Guide Writing**: Share your Pokemon knowledge
- **Team Showcases**: Highlight your best teams
- **Achievements**: Share your accomplishments
- **Fan Art**: Post Pokemon-related artwork

### 🏅 Leaderboards
- **Ranked Battles**: Compete for top rankings
- **Team Shares**: Most popular team creators
- **Tournament Wins**: Championship leaderboard
- **Community Rep**: Most helpful community members

## Getting Started

### Registration

1. Launch the Pokemon Team Builder
2. Click "🌟 Social Hub" in the main menu
3. Click "Register" tab in the login dialog
4. Fill in the registration form:
   - **Username**: 3-20 characters, alphanumeric + underscores
   - **Email**: Valid email address for verification
   - **Display Name**: Your public name
   - **Password**: Minimum 6 characters (stronger recommended)
   - **Bio**: Optional description about yourself

5. Click "Create Account"
6. Check your email for verification link (or check `logs/email_verifications.txt` in demo mode)
7. Click the verification link to activate your account

### Login

1. Open Social Hub
2. Enter your username or email
3. Enter your password
4. Click "Login"

### Demo Accounts

For testing, use these pre-created accounts:

| Username | Password | Role |
|----------|----------|------|
| demo_user | demo123 | General User |
| ash_ketchum | pikachu123 | Demo Trainer |
| misty_waterflower | starmie123 | Gym Leader |
| brock_harrison | onix123 | Breeder |

## Username System

### Username Rules
- **Length**: 3-20 characters
- **Characters**: Letters (a-z, A-Z), numbers (0-9), underscores (_)
- **Uniqueness**: Case-insensitive (ASH = ash = Ash)
- **No Spaces**: Use underscores instead
- **No Special Characters**: Only alphanumeric and underscores

### Valid Examples
✅ `ash_ketchum`
✅ `MistyWater123`
✅ `Brock_2024`
✅ `pokemon_master`

### Invalid Examples
❌ `as` (too short)
❌ `ash ketchum` (contains space)
❌ `ash-ketchum` (contains hyphen)
❌ `ash.ketchum` (contains period)
❌ `this_is_a_very_long_username_123` (too long)

## Email Verification

### Why Verify Your Email?

1. **Account Recovery**: Reset your password if you forget it
2. **Security**: Prevent unauthorized account creation
3. **Notifications**: Receive important community updates
4. **Trust**: Verified accounts are more trustworthy

### Verification Process

1. **Automatic**: Verification email sent upon registration
2. **Link Expires**: Verification links expire after 24 hours
3. **Resend Option**: Request a new link if yours expires
4. **One-Time**: Only need to verify once per account

### Verification Link Format
```
http://localhost:5000/verify-email?token=abc123...
```

### Checking Verification Status
Your profile will show:
- ✅ **Email Verified** - Account fully activated
- ⚠️ **Email Pending** - Check your email for verification link

## Security Features

### Password Protection
- **Hashing**: Passwords are never stored in plain text
- **SHA-256**: Industry-standard encryption
- **Strength Meter**: Real-time password strength feedback
- **Minimum Length**: 6 characters (8+ recommended)

### Account Protection
- **Unique Usernames**: No duplicate usernames allowed
- **Unique Emails**: One account per email address
- **Session Management**: Secure login sessions
- **Status Tracking**: Monitor account activity

### Privacy
- **Public Profiles**: Display name and bio are public
- **Private Email**: Email addresses are never shown publicly
- **Friend Privacy**: Control who can see your friends list
- **Team Privacy**: Choose to share teams publicly or privately

## Community Guidelines

### Usernames
- No offensive or inappropriate names
- No impersonation of other users
- No advertising or spam in usernames

### Content
- Be respectful to other trainers
- No inappropriate or offensive content
- Share constructive feedback
- Credit team builders when sharing teams

### Behavior
- No harassment or bullying
- No cheating or exploits
- Help new trainers learn
- Report violations to moderators

## Troubleshooting

### Can't Register
- **Username Taken**: Try a different username
- **Email Already Used**: One account per email
- **Invalid Format**: Check username rules (3-20 chars, alphanumeric + underscores)

### Didn't Receive Verification Email
1. Check spam/junk folder
2. Verify email address is correct
3. Wait a few minutes (email may be delayed)
4. Check `logs/email_verifications.txt` (demo mode)
5. Request a new verification link

### Forgot Password
1. Click "Forgot Password" on login screen (coming soon)
2. Enter your email address
3. Check email for reset link
4. Create a new password

### Username Already Taken
- Try variations: `ash_ketchum` → `ash_ketchum_2024`
- Add numbers: `pikachu` → `pikachu123`
- Use underscores: `ashketchum` → `ash_ketchum`
- Be creative: `ash` → `ash_from_pallet`

## Technical Details

### Database Schema

#### Users Table
```sql
- user_id (PRIMARY KEY)
- username (UNIQUE, NOT NULL)
- email (UNIQUE, NOT NULL)
- email_verified (INTEGER, 0/1)
- verification_token (TEXT)
- verification_sent_date (TIMESTAMP)
- display_name (TEXT)
- password_hash (SHA-256)
- status (online/away/busy/offline)
- level, experience
- badges, achievements
- join_date, last_active
```

### Email Configuration

#### SMTP Settings
For production email sending, configure these in `src/features/social_community_hub.py`:

```python
smtp_server = "smtp.gmail.com"  # Your SMTP server
smtp_port = 587                  # Usually 587 for TLS
sender_email = "your@email.com"  # Sender email
sender_password = "app-password" # App-specific password
```

#### Email Template
HTML email includes:
- Pokemon Team Builder branding
- Personalized greeting
- Verification button
- Plain text link fallback
- Professional styling

## API Reference

### User Management Functions

```python
# Check username availability
is_available = community_manager.is_username_available("ash_ketchum")

# Check email availability  
is_available = community_manager.is_email_available("ash@pokemon.com")

# Register new user
user_id = community_manager.register_user(
    username="ash_ketchum",
    email="ash@pokemon.com", 
    display_name="Ash Ketchum",
    password="pikachu123",
    bio="Pokemon Master in training!"
)

# Authenticate user
user = community_manager.authenticate_user("ash_ketchum", "pikachu123")

# Verify email
success = community_manager.verify_email(verification_token)

# Resend verification
success = community_manager.resend_verification_email("ash@pokemon.com")
```

## Future Features

### Planned Enhancements
- 🔐 Two-Factor Authentication (2FA)
- 📱 Mobile App Integration
- 🖼️ Avatar Upload System
- 💬 Direct Messaging
- 🔔 Push Notifications
- 🌐 Multi-Language Support
- 🎨 Custom Themes per User
- 📊 Advanced Analytics
- 🤖 AI Chatbot Assistant
- 🏪 Community Marketplace

## Support

### Getting Help
- **Documentation**: Read this guide
- **Community**: Ask in discussion forums
- **Bug Reports**: Report issues on GitHub
- **Feature Requests**: Suggest new features

### Contact
- **Email**: support@pokemonteambuilder.com (placeholder)
- **Discord**: Join our community server (coming soon)
- **Twitter**: @PokemonTeamBuilder (placeholder)

---

**Version**: 1.0.0
**Last Updated**: October 26, 2025
**License**: MIT

*Gotta catch 'em all! 🎮*
