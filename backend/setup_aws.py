# AWS Setup Helper Script
# This script helps you create the required AWS resources

import boto3
import json
from pathlib import Path

def load_config():
    """Load AWS configuration"""
    config_path = Path(__file__).parent / 'aws_config.json'
    if not config_path.exists():
        print("Error: aws_config.json not found. Please copy aws_config.json.example to aws_config.json")
        return None
    
    with open(config_path, 'r') as f:
        return json.load(f)

def create_s3_bucket(config):
    """Create S3 bucket if it doesn't exist"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            region_name=config['region']
        )
        
        bucket_name = config['s3_bucket_name']
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ S3 bucket '{bucket_name}' already exists")
            return True
        except:
            pass
        
        # Create bucket
        if config['region'] == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': config['region']}
            )
        
        print(f"✓ Created S3 bucket: {bucket_name}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create S3 bucket: {str(e)}")
        return False

def create_dynamodb_table(config):
    """Create DynamoDB table if it doesn't exist"""
    try:
        dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            region_name=config['region']
        )
        
        table_name = config['dynamodb_table_name']
        
        # Check if table exists
        try:
            dynamodb.describe_table(TableName=table_name)
            print(f"✓ DynamoDB table '{table_name}' already exists")
            return True
        except:
            pass
        
        # Create table
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'file_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'file_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"✓ Created DynamoDB table: {table_name}")
        print("  Waiting for table to be active...")
        
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print("✓ Table is now active")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create DynamoDB table: {str(e)}")
        return False

def main():
    print("AWS Setup Helper")
    print("=" * 50)
    print()
    
    config = load_config()
    if not config:
        return
    
    print("Configuration loaded:")
    print(f"  Region: {config['region']}")
    print(f"  S3 Bucket: {config['s3_bucket_name']}")
    print(f"  DynamoDB Table: {config['dynamodb_table_name']}")
    print()
    
    print("Creating AWS resources...")
    print()
    
    s3_success = create_s3_bucket(config)
    dynamodb_success = create_dynamodb_table(config)
    
    print()
    print("=" * 50)
    if s3_success and dynamodb_success:
        print("✓ Setup complete! All AWS resources are ready.")
    else:
        print("⚠ Some resources failed to create. Please check the errors above.")
    print()

if __name__ == '__main__':
    main()
