"""
Backend Server for Pokemon Team Builder
Handles user registration, email verification, and social features.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import hashlib
import uuid
import os
import sys
import json
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from features.social_community_hub import CommunityManager, UserStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Email configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'pokemonteambuilder@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')  # Set in environment
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

# Initialize Community Manager
community_manager = CommunityManager()

def send_verification_email_smtp(email: str, username: str, token: str) -> bool:
    """Send verification email via SMTP."""
    try:
        verification_link = f"{BASE_URL}/verify-email?token={token}"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Pokemon Team Builder - Verify Your Email"
        message["From"] = SENDER_EMAIL
        message["To"] = email
        
        # HTML email content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #2C3E50; text-align: center;">🎮 Pokemon Team Builder</h1>
                    <h2 style="color: #3498db;">Welcome, {username}!</h2>
                    
                    <p style="font-size: 16px; color: #555;">
                        Thank you for joining the Pokemon Team Builder community! To complete your registration 
                        and verify your email address, please click the button below:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_link}" 
                           style="background-color: #3498db; color: white; padding: 15px 30px; 
                                  text-decoration: none; border-radius: 5px; font-weight: bold; 
                                  display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #777;">
                        Or copy and paste this link into your browser:<br>
                        <a href="{verification_link}" style="color: #3498db;">{verification_link}</a>
                    </p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="font-size: 14px; color: #555; margin: 0;">
                            <strong>Security Note:</strong> This link will expire in 24 hours for your protection.
                        </p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999;">
                        If you didn't create an account, please ignore this email or contact support if you're concerned.
                    </p>
                    
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        © 2025 Pokemon Team Builder. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text fallback
        text_content = f"""
        Pokemon Team Builder - Email Verification
        
        Welcome, {username}!
        
        Thank you for joining the Pokemon Team Builder community! To complete your registration 
        and verify your email address, please visit this link:
        
        {verification_link}
        
        This link will expire in 24 hours for your protection.
        
        If you didn't create an account, please ignore this email.
        
        © 2025 Pokemon Team Builder. All rights reserved.
        """
        
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        if SENDER_PASSWORD:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, message.as_string())
            
            logger.info(f"Verification email sent to {email}")
            return True
        else:
            # Demo mode - save to file
            os.makedirs("logs", exist_ok=True)
            verification_file = os.path.join("logs", "email_verifications.txt")
            
            with open(verification_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Verification Link: {verification_link}\n")
                f.write(f"{'='*60}\n")
            
            logger.info(f"Demo mode: Verification link saved to {verification_file}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


@app.route('/')
def index():
    """API information page."""
    return jsonify({
        'service': 'Pokemon Team Builder Backend API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'POST /api/register': 'Register new user',
            'POST /api/login': 'Authenticate user',
            'GET /api/user/<user_id>': 'Get user profile',
            'POST /api/verify-email': 'Verify email with token',
            'POST /api/resend-verification': 'Resend verification email',
            'GET /api/check-username/<username>': 'Check username availability',
            'GET /api/check-email/<email>': 'Check email availability',
            'GET /verify-email': 'Email verification page (browser)'
        }
    })


@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user and send verification email."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'display_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        display_name = data['display_name'].strip()
        bio = data.get('bio', 'Pokemon Trainer').strip()
        
        # Validate username format
        if not community_manager._validate_username(username):
            return jsonify({
                'error': 'Invalid username format. Must be 3-20 characters, alphanumeric and underscores only.'
            }), 400
        
        # Check username availability
        if not community_manager.is_username_available(username):
            return jsonify({'error': 'Username already taken'}), 409
        
        # Check email availability
        if not community_manager.is_email_available(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Validate password length
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Register user
        user_id = community_manager.register_user(
            username=username,
            email=email,
            display_name=display_name,
            password=password,
            bio=bio
        )
        
        if not user_id:
            return jsonify({'error': 'Registration failed'}), 500
        
        # Get verification token
        cursor = community_manager.database.connection.cursor()
        cursor.execute(
            "SELECT verification_token FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        verification_token = row['verification_token'] if row else None
        
        # Send verification email via SMTP
        email_sent = False
        if verification_token:
            email_sent = send_verification_email_smtp(email, username, verification_token)
        
        logger.info(f"User registered: {username} (ID: {user_id})")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': username,
            'email_sent': email_sent,
            'message': 'Registration successful! Please check your email to verify your account.'
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/login', methods=['POST'])
def login_user():
    """Authenticate user."""
    try:
        data = request.json
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        username_or_email = data['username'].strip()
        password = data['password']
        
        # Authenticate
        user = community_manager.authenticate_user(username_or_email, password)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update status to online
        community_manager.update_user_status(user.user_id, UserStatus.ONLINE)
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'display_name': user.display_name,
                'bio': user.bio,
                'level': user.level,
                'experience': user.experience,
                'status': user.status.value,
                'badges': user.badges,
                'achievements': user.achievements
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile by ID."""
    try:
        user = community_manager.get_user(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'display_name': user.display_name,
                'bio': user.bio,
                'level': user.level,
                'experience': user.experience,
                'status': user.status.value,
                'badges': user.badges,
                'achievements': user.achievements,
                'join_date': user.join_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/verify-email', methods=['POST'])
def verify_email_api():
    """Verify email with token (API endpoint)."""
    try:
        data = request.json
        
        if 'token' not in data:
            return jsonify({'error': 'Missing verification token'}), 400
        
        token = data['token']
        success = community_manager.verify_email(token)
        
        if success:
            logger.info(f"Email verified with token: {token[:10]}...")
            return jsonify({
                'success': True,
                'message': 'Email verified successfully!'
            }), 200
        else:
            return jsonify({
                'error': 'Invalid or expired verification token'
            }), 400
            
    except Exception as e:
        logger.error(f"Verify email error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/verify-email', methods=['GET'])
def verify_email_page():
    """Email verification page (browser access)."""
    token = request.args.get('token')
    
    if not token:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verification - Pokemon Team Builder</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #e74c3c; }
                .icon { font-size: 64px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">❌</div>
                <h1>Invalid Verification Link</h1>
                <p>The verification link is missing the required token.</p>
            </div>
        </body>
        </html>
        """), 400
    
    # Verify the token
    success = community_manager.verify_email(token)
    
    if success:
        logger.info(f"Email verified via browser: {token[:10]}...")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verified - Pokemon Team Builder</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #27ae60; }
                .icon { font-size: 64px; margin-bottom: 20px; }
                .button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .button:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✅</div>
                <h1>Email Verified!</h1>
                <p>Your email has been successfully verified.</p>
                <p>You can now access all features of Pokemon Team Builder.</p>
                <a href="#" class="button" onclick="window.close()">Close Window</a>
            </div>
        </body>
        </html>
        """), 200
    else:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification Failed - Pokemon Team Builder</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #e74c3c; }
                .icon { font-size: 64px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">⚠️</div>
                <h1>Verification Failed</h1>
                <p>The verification link is invalid or has expired.</p>
                <p>Verification links expire after 24 hours.</p>
                <p>Please request a new verification email from the app.</p>
            </div>
        </body>
        </html>
        """), 400


@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email."""
    try:
        data = request.json
        
        if 'email' not in data:
            return jsonify({'error': 'Missing email address'}), 400
        
        email = data['email'].strip()
        
        # Get user info
        cursor = community_manager.database.connection.cursor()
        cursor.execute(
            "SELECT user_id, username, email_verified, verification_token FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Email not found'}), 404
        
        if row['email_verified']:
            return jsonify({'error': 'Email already verified'}), 400
        
        # Resend verification
        success = community_manager.resend_verification_email(email)
        
        if success:
            # Get new token and send email
            cursor.execute(
                "SELECT verification_token FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            if row:
                send_verification_email_smtp(email, row['username'], row['verification_token'])
            
            return jsonify({
                'success': True,
                'message': 'Verification email sent successfully!'
            }), 200
        else:
            return jsonify({'error': 'Failed to resend verification email'}), 500
            
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/check-username/<username>', methods=['GET'])
def check_username(username):
    """Check if username is available."""
    try:
        available = community_manager.is_username_available(username)
        valid = community_manager._validate_username(username)
        
        return jsonify({
            'username': username,
            'available': available,
            'valid': valid
        }), 200
        
    except Exception as e:
        logger.error(f"Check username error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/check-email/<email>', methods=['GET'])
def check_email(email):
    """Check if email is available."""
    try:
        available = community_manager.is_email_available(email)
        
        return jsonify({
            'email': email,
            'available': available
        }), 200
        
    except Exception as e:
        logger.error(f"Check email error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Pokemon Team Builder Backend',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    logger.info("Starting Pokemon Team Builder Backend Server...")
    logger.info(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    logger.info(f"Sender Email: {SENDER_EMAIL}")
    logger.info(f"Email Mode: {'Production (SMTP)' if SENDER_PASSWORD else 'Demo (File)'}")
    logger.info(f"Base URL: {BASE_URL}")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
