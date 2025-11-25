import boto3
import uuid
from datetime import datetime
from config import Config

class S3Service:
    """Service for uploading files to AWS S3"""
    
    def __init__(self):
        self.s3_client = boto3.client('s3', **Config.get_aws_credentials())
        self.bucket_name = Config.get_s3_bucket_name()
    
    def upload_file(self, file_obj, original_filename, username):
        """
        Upload a file to S3
        
        Args:
            file_obj: File object to upload
            original_filename: Original name of the file
            username: Username of the uploader
            
        Returns:
            dict: Contains s3_key and s3_url
        """
        try:
            # Generate unique file key
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            file_extension = original_filename.rsplit('.', 1)[1] if '.' in original_filename else ''
            s3_key = f"uploads/{username}/{timestamp}_{unique_id}.{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': file_obj.content_type if hasattr(file_obj, 'content_type') else 'application/octet-stream'}
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{Config.get_aws_credentials()['region_name']}.amazonaws.com/{s3_key}"
            
            return {
                'success': True,
                's3_key': s3_key,
                's3_url': s3_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to upload to S3: {str(e)}'
            }
    
    def delete_file(self, s3_key):
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
