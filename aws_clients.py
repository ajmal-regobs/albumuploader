import boto3
from config import AWS_REGION

session = boto3.session.Session(region_name=AWS_REGION)

s3 = session.client("s3")
sqs = session.client("sqs")
dynamodb = session.resource("dynamodb")
