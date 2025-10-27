# Admin Panel Quick Reference

## Quick Access

**Launch Admin Panel:**
1. Start the application: `python run_gui.py`
2. Click "🔒 Admin Panel" button in navigation
3. Enter admin password (default: `admin123`)

---

## Default Credentials

```
Admin PIN: 050270
```

⚠️ **IMPORTANT:** Keep this PIN secure and confidential!

---

## Main Features

### 📊 Dashboard
- System statistics at a glance
- Recent user activity
- Quick action buttons

### 👥 Users
- Search and manage users
- View user details
- Verify emails manually
- Delete/ban users

### 📝 Content
- Review recent posts
- Moderate community content
- Delete inappropriate posts

### 📈 Statistics
- Comprehensive system metrics
- User engagement data
- Database size info

### 💾 Database
- Create backups
- Optimize performance
- Export to JSON
- View schema

### ⚙️ Settings
- Change admin password
- Configure SMTP
- System maintenance

---

## Common Tasks

### Manually Verify User Email

```
1. Users tab → Search for user
2. Select user from list
3. Click "Verify Email" button
4. Confirmation message appears
```

### Create Database Backup

```
1. Database tab
2. Click "Backup Database"
3. Backup saved to: backups/social_community_YYYYMMDD_HHMMSS.db
```

### Delete User Account

```
1. Users tab → Search for user
2. Select user from list
3. Click "Delete User" button
4. Confirm deletion (⚠️ Cannot be undone!)
```

### View System Logs

```
1. Dashboard tab
2. Click "View Logs" button
3. Logs located in: logs/
   - email_verifications.txt
   - application.log
   - error.log
```

---

## Security Notes

### Change Admin PIN (If Needed)

Edit `src/gui/admin_panel_gui.py`:

```python
# In _handle_login method, replace:
if password == "050270":

# With your new PIN:
if password == "YOUR_NEW_PIN":
```

### Secure PIN Storage (Production)

For enhanced security, use hashed PIN storage:

```python
import hashlib

# Hash PIN
pin_hash = hashlib.sha256("050270".encode()).hexdigest()

# Verify login
input_hash = hashlib.sha256(input_pin.encode()).hexdigest()
if input_hash == pin_hash:
    # Grant access
```

---

## Troubleshooting

### Can't Login
- Check password is correct (default: `admin123`)
- Verify `social_community.db` exists
- Check for errors in console

### No Users Showing
- Ensure database is initialized
- Run: `python initialize_social_database.py`
- Check Users tab with "Show All"

### Statistics Show Zero
- Database may be empty
- Create demo users: `initialize_social_database.py`
- Click "Refresh Stats" on Dashboard

---

## Full Documentation

See **ADMIN_PANEL_GUIDE.md** for complete documentation.

---

**Admin PIN:** `050270` (⚠️ Keep secure!)
**Access:** Click "🔒 Admin Panel" button in main app
