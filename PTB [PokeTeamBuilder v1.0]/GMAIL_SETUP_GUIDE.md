# Gmail SMTP Setup Guide for Pokemon Team Builder

## Why Gmail?
Gmail provides free, reliable SMTP service perfect for sending verification emails. It's easy to set up and works great for small to medium applications.

## Prerequisites
- Gmail account
- 2-Step Verification enabled

## Step-by-Step Setup

### Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google," click **2-Step Verification**
4. Click **Get Started**
5. Follow the prompts to set up 2-Step Verification using:
   - Your phone number (recommended)
   - Google Authenticator app
   - Security key

### Step 2: Generate App Password

1. After enabling 2-Step Verification, go to: https://myaccount.google.com/apppasswords
   
   Or navigate:
   - Google Account → Security → 2-Step Verification → App passwords

2. You may need to sign in again

3. Under "Select app," choose **Mail**

4. Under "Select device," choose:
   - **Windows Computer** (if on Windows)
   - **Mac** (if on Mac)
   - **Other (Custom name)** - enter "Pokemon Team Builder"

5. Click **Generate**

6. Google will display a 16-character password like:
   ```
   xxxx xxxx xxxx xxxx
   ```

7. **IMPORTANT**: Copy this password immediately!
   - You won't be able to see it again
   - Remove all spaces when using it
   - Example: `xxxxxxxxxxxxxxxx` (no spaces)

### Step 3: Configure Pokemon Team Builder

1. **Copy the configuration template:**
   ```bash
   copy .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   notepad .env
   ```

3. **Update these lines:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password-here
   ```

4. **Replace:**
   - `your-email@gmail.com` → Your actual Gmail address
   - `your-16-char-app-password-here` → Your 16-character app password (NO SPACES)

5. **Save the file**

### Step 4: Test the Configuration

1. **Start the backend server:**
   ```bash
   python start_backend.py
   ```

2. **You should see:**
   ```
   Email Mode: ✓ Production (SMTP configured)
   ```

3. **Run the test:**
   ```bash
   python test_backend.py
   ```

4. **Register a test user in the GUI**
   - You should receive a real email!

## Example .env File

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=pokemonbuilder2024@gmail.com
SENDER_PASSWORD=your-16-char-app-password-here

# Server Configuration
BASE_URL=http://localhost:5000
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

## Troubleshooting

### "Username and Password not accepted"

**Problem:** Gmail rejects login

**Solutions:**
1. Make sure 2-Step Verification is enabled
2. Use App Password, not your regular Gmail password
3. Remove all spaces from the 16-character password
4. Generate a new App Password if needed

### "App Passwords not available"

**Problem:** Can't find App Passwords option

**Solutions:**
1. Verify 2-Step Verification is fully enabled
2. Wait 24 hours after enabling 2-Step Verification
3. Make sure you're using your personal Gmail (not G Suite/Workspace)
4. Try accessing directly: https://myaccount.google.com/apppasswords

### Email not sending but no error

**Problem:** Server starts but emails don't arrive

**Solutions:**
1. Check spam/junk folder
2. Verify SENDER_EMAIL matches the Gmail account
3. Check Gmail sent folder to confirm email was sent
4. Wait a few minutes (Gmail may delay first emails)

### "Less secure app access"

**Problem:** Old tutorial mentions "less secure apps"

**Note:** Google removed this option in May 2022. You MUST use:
- 2-Step Verification + App Password (recommended)
- OAuth 2.0 (advanced)

### Testing Gmail SMTP Directly

```python
import smtplib

# Test SMTP connection
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
server.quit()
print("✓ Gmail SMTP configured correctly!")
```

## Security Best Practices

### ✅ DO:
- Use App Passwords (not your main password)
- Keep .env file private (add to .gitignore)
- Use different App Passwords for different apps
- Revoke unused App Passwords
- Enable 2-Step Verification

### ❌ DON'T:
- Share your App Password
- Commit .env to Git/GitHub
- Use your main Gmail password
- Disable 2-Step Verification
- Share your .env file

## Managing App Passwords

### View Existing App Passwords
1. Go to: https://myaccount.google.com/apppasswords
2. You'll see a list of generated passwords
3. Names show which apps use them

### Revoke App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Click the **X** next to the password you want to remove
3. Confirm removal

### When to Generate New Password
- If you suspect password was compromised
- When setting up app on new device
- If you lost/forgot the original password
- For better organization (one per app)

## Alternative Email Providers

If you don't want to use Gmail:

### Outlook.com / Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yahoo.com
SENDER_PASSWORD=your-app-password
```
Note: Yahoo also requires app passwords

### SendGrid (Professional)
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
```

## Email Sending Limits

### Gmail Free Account
- **Daily limit**: 500 emails/day
- **Per hour**: ~100 emails/hour
- **Burst**: ~20 emails/minute

For Pokemon Team Builder, this is more than enough!

### What counts as an email?
- Registration verification
- Password reset
- Notifications
- Friend requests (if implemented)

## FAQ

**Q: Do I need a new Gmail account?**
A: No, you can use your existing Gmail. But creating a dedicated account (e.g., pokemonbuilder@gmail.com) is recommended for organization.

**Q: Will this work with G Suite / Google Workspace?**
A: Yes, but your admin might need to enable less secure apps or App Passwords.

**Q: Can I send from a different email than my Gmail?**
A: No, you must send from the Gmail account you're authenticating with.

**Q: Is this free?**
A: Yes! Gmail SMTP is completely free for personal use.

**Q: What if I hit the sending limit?**
A: Very unlikely for this app. If needed, create multiple Gmail accounts and rotate them.

**Q: Can I use this in production?**
A: For small applications (< 500 users/day), yes. For larger scale, use SendGrid, AWS SES, or Mailgun.

## Quick Reference Card

```
╔════════════════════════════════════════════╗
║   Gmail SMTP Quick Reference              ║
╠════════════════════════════════════════════╣
║ Server:    smtp.gmail.com                 ║
║ Port:      587                            ║
║ Security:  STARTTLS                       ║
║ Username:  your-email@gmail.com           ║
║ Password:  16-char app password           ║
║ Limit:     500 emails/day                 ║
╚════════════════════════════════════════════╝
```

## Support

If you're still having issues:

1. Check the backend server logs
2. Test SMTP connection directly (Python script above)
3. Verify 2-Step Verification is enabled
4. Generate a fresh App Password
5. Check Gmail's security page for blocked sign-in attempts

---

**Need help?** Create an issue on GitHub with:
- Error message
- Server logs
- Steps you've tried
- Whether 2-Step Verification is enabled

**Working?** Great! Now you can send professional verification emails to all new Pokemon trainers! 🎮

---

*Last updated: October 26, 2025*
