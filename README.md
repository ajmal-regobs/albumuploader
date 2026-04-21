# albumuploader

Simple Python album uploader: HTML UI → Flask → S3 + SQS + DynamoDB.
On upload, the handler stores the image in S3, sends a message to SQS, and writes metadata to DynamoDB — all in one request.

AWS auth uses the default boto3 credential chain, so an attached IAM role (EC2 instance profile, ECS task role, IRSA, or local `AWS_PROFILE`) is used automatically — no keys in code.

## AWS resources you need

- **S3 bucket** — stores the images.
- **SQS queue** — receives an upload event per image.
- **DynamoDB table** — partition key `album` (String), sort key `image_id` (String).

Required env vars: `AWS_REGION`, `S3_BUCKET`, `SQS_QUEUE_URL`, `DYNAMODB_TABLE`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit values
```

## Run

```bash
python app.py
```
Open http://localhost:5000

## Endpoints

- `GET  /` — upload form
- `GET  /health` — liveness check, returns `{"status":"ok"}`
- `POST /upload` — multipart: `image`, `album`, `title`, `description`
- `GET  /albums/<album>` — list metadata for an album

## Docker

```bash
docker build -t albumuploader .
docker run --rm -p 5000:5000 --env-file .env albumuploader
```

Runs gunicorn on port 5000. On AWS (ECS/EKS/EC2), attach the IAM role to the task/pod/instance — no keys needed.
