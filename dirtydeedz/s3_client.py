import boto3
from botocore.client import Config
from .settings import get_env_variable

# Configuration
access_key = get_env_variable('DO_ACCESS_KEY_ID')
secret_key = get_env_variable('DO_SECRET_ACCESS_KEY')
region = 'nayc1' 
endpoint_url = get_env_variable('DO_SPACES_ENDPOINT')

# Initialize session and client
session = boto3.session.Session()
client = session.client(
    's3',
    region_name=region,
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(signature_version='s3v4')
)

# Verify signing method
print(f"Signature Version: {client.meta.config.signature_version}")