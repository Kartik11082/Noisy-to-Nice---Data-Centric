import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from config import Config

class DynamoDBService:
    """Service for storing file metadata in DynamoDB"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', **Config.get_aws_credentials())
        self.table_name = Config.get_dynamodb_table_name()
        self.table = self.dynamodb.Table(self.table_name)
    
    def store_metadata(self, metadata):
        """
        Store file metadata in DynamoDB
        
        Args:
            metadata: Dictionary containing file metadata
            
        Returns:
            dict: Success status and file_id
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Prepare item for DynamoDB
            item = {
                'file_id': file_id,
                'user_id': metadata['user_id'],
                'filename': metadata['filename'],
                'file_size': Decimal(str(metadata['file_size'])),
                'file_type': metadata['file_type'],
                's3_key': metadata['s3_key'],
                's3_url': metadata['s3_url'],
                'upload_timestamp': metadata['upload_timestamp']
            }
            
            # Add CSV-specific metadata if available
            if 'row_count' in metadata:
                item['row_count'] = Decimal(str(metadata['row_count']))
            if 'column_count' in metadata:
                item['column_count'] = Decimal(str(metadata['column_count']))
            if 'columns' in metadata:
                item['columns'] = metadata['columns']
            
            # Store in DynamoDB
            self.table.put_item(Item=item)
            
            return {
                'success': True,
                'file_id': file_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to store metadata in DynamoDB: {str(e)}'
            }
    
    def get_user_files(self, username):
        """Get all files uploaded by a user"""
        try:
            response = self.table.scan(
                FilterExpression='user_id = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            # Convert Decimal to int/float for JSON serialization
            items = response.get('Items', [])
            for item in items:
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = int(value) if value % 1 == 0 else float(value)
            
            return {
                'success': True,
                'files': items
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to fetch files: {str(e)}'
            }
    
    def delete_metadata(self, file_id):
        """Delete file metadata"""
        try:
            self.table.delete_item(Key={'file_id': file_id})
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
