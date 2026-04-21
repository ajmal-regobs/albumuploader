import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ["S3_BUCKET"]
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024
