from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import pandas as pd
import numpy as np
from datetime import datetime
from decimal import Decimal
import io

from config import Config
from services.auth_service import AuthService
from services.s3_service import S3Service
from services.dynamodb_service import DynamoDBService
from services.profiling_service import ProfilingService
from services.bedrock_service import BedrockService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
s3_service = S3Service()
dynamodb_service = DynamoDBService()
profiling_service = ProfilingService(s3_service)
bedrock_service = BedrockService()

def convert_floats_to_decimal(obj):
    """Recursively convert float and numpy types to DynamoDB-compatible types"""
    # Handle numpy integer types
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    # Handle numpy float types
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return Decimal(str(float(obj)))
    # Handle Python float
    elif isinstance(obj, float):
        return Decimal(str(obj))
    # Handle dictionaries recursively
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    # Handle lists recursively
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    # Return as-is for other types
    return obj

def convert_to_python_types(obj):
    """Recursively convert numpy types to native Python types for JSON serialization"""
    # Handle numpy integer types
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    # Handle numpy float types
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    # Handle Decimal (convert to float for JSON)
    elif isinstance(obj, Decimal):
        return float(obj)
    # Handle dictionaries recursively
    elif isinstance(obj, dict):
        return {k: convert_to_python_types(v) for k, v in obj.items()}
    # Handle lists recursively
    elif isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    # Return as-is for other types
    return obj

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

@app.route('/api/analyze/<file_id>', methods=['POST'])
@token_required
def analyze_file(username, file_id):
    """Generate data quality analysis for a file"""
    try:
        # Get file metadata from DynamoDB
        files_result = dynamodb_service.get_user_files(username)
        
        if not files_result['success']:
            return jsonify({'success': False, 'message': 'Failed to fetch file metadata'}), 500
        
        # Find the specific file
        file_metadata = None
        for f in files_result['files']:
            if f['file_id'] == file_id:
                file_metadata = f
                break
        
        if not file_metadata:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Download file from S3 for profiling
        s3_key = file_metadata['s3_key']
        
        # Get file content from S3
        try:
            s3_object = s3_service.s3_client.get_object(
                Bucket=s3_service.bucket_name,
                Key=s3_key
            )
            file_content = s3_object['Body'].read()
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to download file from S3: {str(e)}'
            }), 500
        
        # Generate profiling report
        profiling_result = profiling_service.generate_profile(
            file_content,
            file_metadata['filename']
        )
        
        if not profiling_result['success']:
            return jsonify(profiling_result), 500
        
        # Generate AI insights using Bedrock
        ai_result = bedrock_service.generate_insights(
            file_metadata['filename'],
            profiling_result['metrics'],
            profiling_result['issues']
        )
        
        # Update metadata in DynamoDB with profiling results
        update_metadata = {
            'user_id': username,
            'filename': file_metadata['filename'],
            'file_size': file_metadata['file_size'],
            'file_type': file_metadata['file_type'],
            's3_key': file_metadata['s3_key'],
            's3_url': file_metadata['s3_url'],
            'upload_timestamp': file_metadata['upload_timestamp'],
            'row_count': file_metadata.get('row_count'),
            'column_count': file_metadata.get('column_count'),
            'columns': file_metadata.get('columns', []),
            'profiling_status': 'completed',
            'profiling_report_url': profiling_result['report_url'],
            'profiling_report_key': profiling_result['report_key'],
            'quality_score': profiling_result['metrics']['quality_score'],
            'missing_percentage': profiling_result['metrics']['missing_percentage'],
            'duplicate_rows_count': profiling_result['metrics']['duplicate_rows'],
            'issues': profiling_result['issues'],
            'profiling_metrics': profiling_result['metrics'],
            'ai_insights': {
                'assessment': ai_result.get('assessment', 'Analysis complete'),
                'recommendations': ai_result.get('recommendations', [])
            }
        }
        
        # Store updated metadata
        dynamodb_service.table.update_item(
            Key={'file_id': file_id},
            UpdateExpression="""
                SET profiling_status = :status,
                    profiling_report_url = :url,
                    profiling_report_key = :key,
                    quality_score = :score,
                    missing_percentage = :missing,
                    duplicate_rows_count = :dups,
                    issues = :issues,
                    profiling_metrics = :metrics,
                    ai_insights = :ai
            """,
            ExpressionAttributeValues={
                ':status': 'completed',
                ':url': profiling_result['report_url'],
                ':key': profiling_result['report_key'],
                ':score': convert_floats_to_decimal(profiling_result['metrics']['quality_score']),
                ':missing': convert_floats_to_decimal(profiling_result['metrics']['missing_percentage']),
                ':dups': profiling_result['metrics']['duplicate_rows'],
                ':issues': convert_floats_to_decimal(profiling_result['issues']),
                ':metrics': convert_floats_to_decimal(update_metadata['profiling_metrics']),
                ':ai': update_metadata['ai_insights']
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Analysis completed',
            'profiling_report_url': profiling_result['report_url'],
            'quality_score': convert_to_python_types(profiling_result['metrics']['quality_score']),
            'metrics': convert_to_python_types(profiling_result['metrics']),
            'issues': convert_to_python_types(profiling_result['issues']),
            'ai_insights': update_metadata['ai_insights']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/analysis/<file_id>', methods=['GET'])
@token_required
def get_analysis(username, file_id):
    """Get analysis results for a file"""
    try:
        # Get file metadata from DynamoDB
        files_result = dynamodb_service.get_user_files(username)
        
        if not files_result['success']:
            return jsonify({'success': False, 'message': 'Failed to fetch file metadata'}), 500
        
        # Find the specific file
        file_metadata = None
        for f in files_result['files']:
            if f['file_id'] == file_id:
                file_metadata = f
                break
        
        if not file_metadata:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Check if analysis has been done
        if 'profiling_status' not in file_metadata or file_metadata['profiling_status'] != 'completed':
            return jsonify({
                'success': False,
                'message': 'Analysis not yet completed',
                'status': file_metadata.get('profiling_status', 'not_started')
            }), 404
        
        # Return analysis data
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file_metadata['filename'],
            'profiling_report_url': file_metadata.get('profiling_report_url'),
            'quality_score': convert_to_python_types(file_metadata.get('quality_score')),
            'metrics': convert_to_python_types(file_metadata.get('profiling_metrics', {})),
            'issues': convert_to_python_types(file_metadata.get('issues', [])),
            'ai_insights': file_metadata.get('ai_insights', {})
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get analysis: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Make sure you have copied aws_config.json.example to aws_config.json and filled in your credentials")
    app.run(debug=True, host='0.0.0.0', port=5000)
