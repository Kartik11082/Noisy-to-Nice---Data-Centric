import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# Simple in-memory user store (for demo purposes)
# In production, this should be in a database
users_db = {}

class AuthService:
    """Simple authentication service"""
    
    @staticmethod
    def register_user(username, password):
        """Register a new user"""
        if username in users_db:
            return {'success': False, 'message': 'Username already exists'}
        
        users_db[username] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        return {'success': True, 'message': 'User registered successfully'}
    
    @staticmethod
    def login_user(username, password):
        """Login a user and return JWT token"""
        if username not in users_db:
            return {'success': False, 'message': 'Invalid username or password'}
        
        user = users_db[username]
        
        if not check_password_hash(user['password_hash'], password):
            return {'success': False, 'message': 'Invalid username or password'}
        
        # Generate JWT token
        token = jwt.encode(
            {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        
        return {
            'success': True,
            'token': token,
            'username': username
        }
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return {'success': True, 'username': payload['username']}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid token'}
