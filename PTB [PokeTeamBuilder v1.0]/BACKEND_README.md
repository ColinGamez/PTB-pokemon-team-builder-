# Pokemon Team Builder - Backend Server

## Overview
The backend server handles user registration, email verification, and provides REST API endpoints for the Pokemon Team Builder social community features.

## Features

- ✅ **User Registration API** - RESTful endpoint for creating new accounts
- ✅ **Email Verification** - Automated email sending with verification links
- ✅ **User Authentication** - Secure login with password hashing
- ✅ **Username/Email Validation** - Real-time availability checking
- ✅ **SMTP Integration** - Production-ready email delivery
- ✅ **Demo Mode** - Fallback to file-based verification for testing
- ✅ **CORS Enabled** - Cross-origin requests supported
- ✅ **Health Checks** - Service monitoring endpoints

## Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-cors
```

### 2. Configure Email (Optional for Production)
```bash
# Copy example configuration
copy .env.example .env

# Edit .env with your SMTP credentials
notepad .env
```

### 3. Start the Server
```bash
# Simple start
python backend_server.py

# Or use the startup script
python start_backend.py
```

### 4. Server will run on
```
http://localhost:5000
```

## Email Configuration

### Gmail Setup (Recommended)

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update .env File**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
BASE_URL=http://localhost:5000
```

### Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yahoo.com
SENDER_PASSWORD=your-app-password
```

#### Custom SMTP Server
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-password
```

## API Endpoints

### User Registration
```http
POST /api/register
Content-Type: application/json

{
  "username": "ash_ketchum",
  "email": "ash@pokemon.com",
  "password": "pikachu123",
  "display_name": "Ash Ketchum",
  "bio": "Pokemon Master in training!"
}

Response 201:
{
  "success": true,
  "user_id": "uuid-here",
  "username": "ash_ketchum",
  "email_sent": true,
  "message": "Registration successful! Please check your email to verify your account."
}
```

### User Login
```http
POST /api/login
Content-Type: application/json

{
  "username": "ash_ketchum",
  "password": "pikachu123"
}

Response 200:
{
  "success": true,
  "user": {
    "user_id": "uuid-here",
    "username": "ash_ketchum",
    "email": "ash@pokemon.com",
    "display_name": "Ash Ketchum",
    "level": 1,
    "experience": 0,
    "status": "online"
  }
}
```

### Check Username Availability
```http
GET /api/check-username/ash_ketchum

Response 200:
{
  "username": "ash_ketchum",
  "available": false,
  "valid": true
}
```

### Check Email Availability
```http
GET /api/check-email/ash@pokemon.com

Response 200:
{
  "email": "ash@pokemon.com",
  "available": false
}
```

### Verify Email (API)
```http
POST /api/verify-email
Content-Type: application/json

{
  "token": "verification-token-here"
}

Response 200:
{
  "success": true,
  "message": "Email verified successfully!"
}
```

### Verify Email (Browser)
```http
GET /verify-email?token=verification-token-here

Returns HTML page with verification status
```

### Resend Verification Email
```http
POST /api/resend-verification
Content-Type: application/json

{
  "email": "ash@pokemon.com"
}

Response 200:
{
  "success": true,
  "message": "Verification email sent successfully!"
}
```

### Get User Profile
```http
GET /api/user/{user_id}

Response 200:
{
  "user": {
    "user_id": "uuid-here",
    "username": "ash_ketchum",
    "display_name": "Ash Ketchum",
    "bio": "Pokemon Master in training!",
    "level": 1,
    "experience": 0,
    "status": "online",
    "badges": [],
    "achievements": []
  }
}
```

### Health Check
```http
GET /health

Response 200:
{
  "status": "healthy",
  "service": "Pokemon Team Builder Backend",
  "timestamp": "2025-10-26T12:00:00"
}
```

## Demo Mode vs Production

### Demo Mode (No SMTP Password)
- ✅ All features work except actual email sending
- ✅ Verification links saved to `logs/email_verifications.txt`
- ✅ Perfect for testing and development
- ✅ No email configuration needed

**Example verification file:**
```
============================================================
Date: 2025-10-26 12:00:00
Username: ash_ketchum
Email: ash@pokemon.com
Verification Link: http://localhost:5000/verify-email?token=abc123...
============================================================
```

### Production Mode (SMTP Configured)
- ✅ Real emails sent via SMTP
- ✅ Professional HTML email templates
- ✅ Automatic verification links
- ✅ 24-hour token expiration

## Email Template

The verification email includes:
- 🎮 Pokemon Team Builder branding
- 👤 Personalized greeting with username
- 🔗 One-click verification button
- 📋 Plain text link fallback
- ⏱️ 24-hour expiration notice
- 🔒 Security information
- 📧 Professional footer

## Security Features

### Password Security
- ✅ SHA-256 hashing (never stored plain text)
- ✅ Minimum 6 character requirement
- ✅ Password strength validation in GUI

### Token Security
- ✅ SHA-256 hashed verification tokens
- ✅ 24-hour expiration window
- ✅ One-time use tokens
- ✅ Secure token generation with timestamp

### Database Security
- ✅ Parameterized queries (SQL injection protection)
- ✅ Unique constraints on username/email
- ✅ Email verification tracking
- ✅ Last activity timestamps

### API Security
- ✅ Input validation on all endpoints
- ✅ Proper HTTP status codes
- ✅ Error message sanitization
- ✅ CORS configuration

## Error Handling

### Common Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Invalid credentials |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Username/email taken |
| 500 | Server Error | Check server logs |

### Error Response Format
```json
{
  "error": "Description of what went wrong"
}
```

## Testing

### Test Registration
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "test123",
    "display_name": "Test User"
  }'
```

### Test Username Check
```bash
curl http://localhost:5000/api/check-username/test_user
```

### Test Health Check
```bash
curl http://localhost:5000/health
```

## Deployment

### Local Development
```bash
python backend_server.py
```

### Production (Linux/Mac)
```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend_server:app

# Using systemd service
sudo systemctl start pokemon-backend
```

### Production (Windows)
```bash
# Using waitress
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 backend_server:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors
EXPOSE 5000
CMD ["python", "backend_server.py"]
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SMTP_SERVER | smtp.gmail.com | SMTP server address |
| SMTP_PORT | 587 | SMTP server port |
| SENDER_EMAIL | pokemonteambuilder@gmail.com | Sender email address |
| SENDER_PASSWORD | (empty) | SMTP password/app password |
| BASE_URL | http://localhost:5000 | Base URL for verification links |

## Logs

### Server Logs
```
INFO - User registered: ash_ketchum (ID: uuid-here)
INFO - Verification email sent to ash@pokemon.com
INFO - User logged in: ash_ketchum
INFO - Email verified via browser: abc123...
```

### Email Verification Log (Demo Mode)
```
logs/email_verifications.txt
```

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials**
   ```bash
   # Test SMTP connection
   python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); print('OK')"
   ```

2. **Verify .env file exists and is loaded**
   ```bash
   # Check if SENDER_PASSWORD is set
   echo $SENDER_PASSWORD  # Linux/Mac
   echo %SENDER_PASSWORD%  # Windows
   ```

3. **Check firewall/antivirus**
   - Allow Python through firewall
   - Port 587 must be open

4. **Gmail App Password**
   - Must have 2-Step Verification enabled
   - Use 16-character app password (no spaces)

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Database Locked

```bash
# Close all connections to database
# Restart the backend server
python backend_server.py
```

## Integration with GUI

The GUI automatically connects to the backend when available:

```python
# GUI will use backend API if running
BACKEND_URL = "http://localhost:5000"

# Otherwise falls back to direct database access
```

## Monitoring

### Health Check Endpoint
```bash
# Check if server is running
curl http://localhost:5000/health

# Should return:
# {"status": "healthy", "service": "Pokemon Team Builder Backend", ...}
```

### Server Status
```bash
# Check process
ps aux | grep backend_server  # Linux/Mac
tasklist | findstr python     # Windows
```

## Performance

- ✅ Handles 100+ concurrent requests
- ✅ Fast database queries with indexing
- ✅ Async email sending (non-blocking)
- ✅ Connection pooling for SMTP

## Support

### Documentation
- README.md (this file)
- SOCIAL_HUB_GUIDE.md (user guide)
- .env.example (configuration template)

### Common Issues
- Email not sending → Check SMTP configuration
- Port in use → Change PORT in .env
- Database errors → Restart server
- Token expired → Request new verification email

## License

MIT License - See LICENSE file

---

**Made with ❤️ for Pokemon Trainers**

*Gotta catch 'em all! 🎮*
