from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import pandas as pd
from datetime import datetime
import io

from config import Config
from services.auth_service import AuthService
from services.s3_service import S3Service
from services.dynamodb_service import DynamoDBService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
s3_service = S3Service()
dynamodb_service = DynamoDBService()

def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        result = AuthService.verify_token(token)
        
        if not result['success']:
            return jsonify(result), 401
        
        # Add username to kwargs
        kwargs['username'] = result['username']
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    result = AuthService.register_user(data['username'], data['password'])
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    result = AuthService.login_user(data['username'], data['password'])
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(username):
    """Upload a file to S3 and store metadata in DynamoDB"""
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    # Validate file type (CSV only)
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'message': 'Only CSV files are allowed'}), 400
    
    try:
        # Read file content for metadata extraction
        file_content = file.read()
        file_size = len(file_content)
        
        # Extract CSV metadata
        csv_metadata = {}
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            csv_metadata = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist()
            }
        except Exception as e:
            # If CSV parsing fails, continue without metadata
            print(f"Warning: Could not parse CSV metadata: {str(e)}")
        
        # Reset file pointer for upload
        file.seek(0)
        
        # Upload to S3
        upload_result = s3_service.upload_file(file, file.filename, username)
        
        if not upload_result['success']:
            return jsonify(upload_result), 500
        
        # Prepare metadata for DynamoDB
        metadata = {
            'user_id': username,
            'filename': file.filename,
            'file_size': file_size,
            'file_type': file.content_type or 'text/csv',
            's3_key': upload_result['s3_key'],
            's3_url': upload_result['s3_url'],
            'upload_timestamp': datetime.utcnow().isoformat(),
            **csv_metadata
        }
        
        # Store metadata in DynamoDB
        db_result = dynamodb_service.store_metadata(metadata)
        
        if not db_result['success']:
            # If DynamoDB fails, optionally delete from S3
            # s3_service.delete_file(upload_result['s3_key'])
            return jsonify(db_result), 500
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_id': db_result['file_id'],
            's3_url': upload_result['s3_url'],
            'metadata': csv_metadata
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/files', methods=['GET'])
@token_required
def get_files(username):
    """Get all files uploaded by the current user"""
    result = dynamodb_service.get_user_files(username)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/files/<file_id>', methods=['DELETE'])
@token_required
def delete_file(username, file_id):
    """Delete a file (metadata only, S3 cleanup optional)"""
    result = dynamodb_service.delete_metadata(file_id)
    
    if result['success']:
        return jsonify({'success': True, 'message': 'File deleted'}), 200
    else:
        return jsonify(result), 500

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Make sure you have copied aws_config.json.example to aws_config.json and filled in your credentials")
    app.run(debug=True, host='0.0.0.0', port=5000)
