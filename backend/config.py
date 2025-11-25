import json
import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # AWS config
    _aws_config = None
    
    @classmethod
    def load_aws_config(cls):
        """Load AWS configuration from aws_config.json"""
        if cls._aws_config is None:
            config_path = Path(__file__).parent / 'aws_config.json'
            
            if not config_path.exists():
                raise FileNotFoundError(
                    f"AWS configuration file not found at {config_path}. "
                    "Please copy aws_config.json.example to aws_config.json and fill in your credentials."
                )
            
            with open(config_path, 'r') as f:
                cls._aws_config = json.load(f)
        
        return cls._aws_config
    
    @classmethod
    def get_aws_credentials(cls):
        """Get AWS credentials"""
        config = cls.load_aws_config()
        return {
            'aws_access_key_id': config['aws_access_key_id'],
            'aws_secret_access_key': config['aws_secret_access_key'],
            'region_name': config['region']
        }
    
    @classmethod
    def get_s3_bucket_name(cls):
        """Get S3 bucket name"""
        config = cls.load_aws_config()
        return config['s3_bucket_name']
    
    @classmethod
    def get_dynamodb_table_name(cls):
        """Get DynamoDB table name"""
        config = cls.load_aws_config()
        return config['dynamodb_table_name']
