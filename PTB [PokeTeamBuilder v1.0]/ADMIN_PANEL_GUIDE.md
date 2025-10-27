# Admin Panel Guide

## Overview

The Admin Panel provides comprehensive tools for managing users, moderating content, monitoring system health, and maintaining the Pokemon Team Builder application.

## Access

### Admin Login

**Admin PIN:** `050270`

⚠️ **IMPORTANT:** Keep this PIN secure and confidential!

### Security Recommendations

1. **Keep PIN Secure:** Never share the admin PIN (050270)
2. **Access Logging:** Log all admin actions for audit trails
3. **Secure Storage:** Store PIN in encrypted configuration file for production
4. **Two-Factor Authentication:** Implement 2FA for production use
5. **Change PIN Regularly:** Update the PIN periodically for enhanced security

---

## Dashboard Tab 📊

The dashboard provides a quick overview of system health and activity.

### Statistics Cards

- **Total Users:** All registered users
- **Online Users:** Currently active users
- **Total Posts:** Community posts created
- **Email Verified:** Users with verified email addresses

### Recent Activity

- View latest user registrations
- Check email verification status (✓/✗)
- Monitor join dates and activity

### Quick Actions

**Refresh Stats:** Update all statistics in real-time

**Export Data:** Export system data
- User list to CSV
- Posts to JSON
- Database backups
- Generate reports

**View Logs:** Access system logs
- `email_verifications.txt` - Email verification links (demo mode)
- `application.log` - General application logs
- `error.log` - Error tracking

---

## Users Tab 👥

Comprehensive user management interface.

### Search Users

Search by:
- Username
- Email address
- Display name

**Show All:** Display complete user list

### User List Columns

| Column | Description |
|--------|-------------|
| Username | Unique username (3-20 chars) |
| Display Name | Public display name |
| Email | User email address |
| Level | User level/rank |
| Status | online/offline/banned |
| Verified | Email verification status (✓/✗) |
| Join Date | Registration timestamp |

### User Actions

**View Details:** See complete user information
- All database fields
- Registration details
- Profile information
- Activity history

**Delete User:** Permanently remove user
- ⚠️ **WARNING:** Cannot be undone!
- Removes all user data
- Deletes associated content
- Confirmation required

**Verify Email:** Manually verify user's email
- Bypass email verification process
- Useful for troubleshooting
- Updates `email_verified` to `1`

**Ban User:** Suspend user account
- Prevent login access
- Hide user content
- Log ban reason
- Reversible action

---

## Content Moderation Tab 📝

Monitor and moderate community content.

### Recent Posts

View latest community posts with:
- Post title and type
- Author information
- Creation timestamp
- Quick action buttons

### Post Actions

**View:** Review full post content
- Read complete post
- Check attachments
- See engagement metrics

**Delete:** Remove inappropriate content
- Removes post from community
- Logs deletion action
- Notifies author (optional)

### Content Types

- **Team Shares:** Shared Pokemon teams
- **Battle Replays:** Recorded battles
- **Discussions:** Community discussions
- **Tournament Posts:** Tournament related

---

## Statistics Tab 📈

Detailed system analytics and metrics.

### User Statistics

```
Total Users: [count]
Verified Users: [count]
Online Users: [count]
```

### Content Statistics

```
Total Posts: [count]
Shared Teams: [count]
Battle Replays: [count]
```

### Social Statistics

```
Total Friendships: [count]
Active Friendships: [count]
Friend Requests: [count]
```

### Database Statistics

```
Database Size: [KB]
Total Tables: [count]
Total Records: [count]
```

---

## Database Tab 💾

Database management and maintenance tools.

### Backup Database

Creates timestamped backup:
- Location: `backups/social_community_YYYYMMDD_HHMMSS.db`
- Full database copy
- Preserves all data
- Safe restoration point

**Backup Schedule Recommendations:**
- Daily backups for production
- Before major updates
- After bulk data imports
- Before database maintenance

### Optimize Database

Runs SQLite VACUUM command:
- Reclaims unused space
- Defragments database
- Improves performance
- Compacts file size

**When to Optimize:**
- After large deletions
- Weekly maintenance
- When performance degrades
- File size bloat

### Export to JSON

Export database tables to JSON format:
- Location: `exports/users_YYYYMMDD_HHMMSS.json`
- Human-readable format
- Data portability
- Integration friendly

**Export Uses:**
- Data migration
- External analysis
- Backup verification
- API integration

### View Database Schema

Display complete database structure:
- All table definitions
- Column types and constraints
- Indexes and keys
- Relationships

---

## Settings Tab ⚙️

Admin configuration and system settings.

### Change Admin PIN

Update admin authentication PIN:
1. Open `src/gui/admin_panel_gui.py`
2. Find the `_handle_login` method
3. Update the PIN check: `if password == "YOUR_NEW_PIN":`
4. Save and restart the application
5. Test with new PIN

**Current PIN Location:**
```python
def _handle_login(self):
    """Handle admin login."""
    password = self.password_var.get()
    
    # Check against secure PIN
    if password == "050270":  # Change this PIN
        self.admin_authenticated = True
        # ... rest of code
```

**Production Implementation:**
For enhanced security, store the PIN hash:
```python
import hashlib

# Hash the PIN
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Store hashed PIN
ADMIN_PIN_HASH = hash_pin("050270")

# Verify login
input_hash = hashlib.sha256(input_pin.encode()).hexdigest()
is_valid = (input_hash == ADMIN_PIN_HASH)
```

### Configure SMTP

Email server settings configuration:

**Gmail Setup:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Outlook Setup:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

See `GMAIL_SETUP_GUIDE.md` for detailed instructions.

### Clear Old Logs

Maintenance task to remove old log files:
- Delete logs older than 30 days
- Archive important logs
- Free disk space
- Prevent log bloat

---

## Security Best Practices

### Admin Access

1. **Limit Admin Accounts:** Only trusted personnel
2. **Unique Passwords:** Different from user accounts
3. **Regular Rotation:** Change passwords quarterly
4. **Access Logging:** Track all admin actions
5. **IP Restrictions:** Limit access by IP (production)

### Data Protection

1. **Regular Backups:** Automated daily backups
2. **Encryption:** Encrypt sensitive data
3. **Secure Deletion:** Properly remove deleted data
4. **Access Controls:** Role-based permissions
5. **Audit Trail:** Log all data modifications

### User Privacy

1. **Minimal Data:** Only collect necessary information
2. **Secure Storage:** Hash passwords, encrypt PII
3. **Data Retention:** Delete old/unused data
4. **GDPR Compliance:** Honor user data requests
5. **Transparency:** Clear privacy policies

---

## Common Admin Tasks

### New User Registration Issue

**Problem:** User can't verify email

**Solution:**
1. Go to Users tab
2. Search for username/email
3. Click "Verify Email" button
4. Notify user verification complete

### Inappropriate Content

**Problem:** User reported offensive post

**Solution:**
1. Go to Content Moderation tab
2. Find reported post
3. Review content
4. Click "Delete" if violates policy
5. Consider warning/banning user

### Database Growing Too Large

**Problem:** Database file exceeds expected size

**Solution:**
1. Go to Database tab
2. Check database statistics
3. Click "Optimize Database"
4. Consider archiving old data
5. Create backup before changes

### User Account Locked

**Problem:** User forgot password, locked out

**Solution:**
1. Verify user identity (security questions)
2. Go to Users tab
3. Find user account
4. Manually reset password
5. Email temporary password
6. Force password change on login

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Daily:**
- New user registrations
- Email verification rate
- Online user count
- Error log entries

**Weekly:**
- Database size growth
- Storage capacity
- Popular content
- User engagement

**Monthly:**
- Total user growth
- Content creation trends
- System performance
- Security incidents

### Alert Thresholds

Set up monitoring for:
- **High Error Rate:** >10 errors/hour
- **Database Size:** >80% capacity
- **Failed Logins:** >5 attempts/user
- **Low Verification:** <50% email verified
- **Disk Space:** <20% free space

---

## Troubleshooting

### Admin Panel Won't Load

**Check:**
1. Database connection (`data/social_community.db` exists)
2. Import paths correct
3. GUI dependencies installed
4. No syntax errors in logs

### Can't Login to Admin Panel

**Solutions:**
1. Verify admin password correct
2. Check login logic in code
3. Reset to default password
4. Review authentication logs

### User List Not Loading

**Debug:**
1. Check database connection
2. Verify users table exists
3. Run: `SELECT * FROM users LIMIT 10`
4. Check for SQL errors in logs

### Statistics Show Zero

**Verify:**
1. Database has data: `SELECT COUNT(*) FROM users`
2. Query logic correct
3. Database initialized properly
4. Connection active

---

## API Integration (Future)

The admin panel can be extended with REST API endpoints:

### Proposed Endpoints

```
GET  /admin/stats              - System statistics
GET  /admin/users              - List all users
GET  /admin/users/:id          - Get user details
PUT  /admin/users/:id          - Update user
DELETE /admin/users/:id        - Delete user
GET  /admin/posts              - List all posts
DELETE /admin/posts/:id        - Delete post
POST /admin/backup             - Create backup
GET  /admin/logs               - Get system logs
```

### Authentication

Use JWT tokens for API access:
```python
import jwt

token = jwt.encode(
    {'admin_id': admin_id, 'exp': expiration},
    SECRET_KEY,
    algorithm='HS256'
)
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change default admin password
- [ ] Configure SMTP for email sending
- [ ] Set up automated backups
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring/alerts
- [ ] Document admin procedures
- [ ] Train admin staff
- [ ] Test disaster recovery
- [ ] Review security policies

### Environment Variables

Create `.env.admin` file:
```env
ADMIN_PASSWORD_HASH=<bcrypt_hash>
ADMIN_SESSION_TIMEOUT=3600
ADMIN_MAX_LOGIN_ATTEMPTS=3
ADMIN_LOCKOUT_DURATION=300
ADMIN_REQUIRE_2FA=true
```

### Logging Configuration

Production logging setup:
```python
logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/admin.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
```

---

## Support

### Getting Help

**Documentation:**
- `README.md` - General application guide
- `BACKEND_README.md` - Backend server documentation
- `GMAIL_SETUP_GUIDE.md` - Email configuration
- `SOCIAL_HUB_GUIDE.md` - Social features guide

**Troubleshooting:**
1. Check error logs in `logs/` directory
2. Review database integrity
3. Verify configuration files
4. Test with demo data

### Reporting Issues

When reporting admin panel issues, include:
1. Error messages from logs
2. Steps to reproduce
3. Expected vs actual behavior
4. System configuration
5. Database statistics

---

## Version History

**v1.0** - Initial Release
- Dashboard with system overview
- User management interface
- Content moderation tools
- Database maintenance
- Admin settings panel

---

## Future Enhancements

Planned improvements:
- [ ] Role-based admin permissions (Super Admin, Moderator, Support)
- [ ] Advanced analytics and reporting
- [ ] Bulk user operations
- [ ] Automated moderation rules
- [ ] Email template customization
- [ ] Two-factor authentication
- [ ] Activity audit log viewer
- [ ] Real-time notifications
- [ ] Dashboard widgets customization
- [ ] Export to multiple formats (CSV, Excel, PDF)

---

**Last Updated:** October 26, 2025
**Version:** 1.0
**Status:** Production Ready
