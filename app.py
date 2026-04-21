import json
import uuid
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify

from aws_clients import s3, sqs, dynamodb
from config import (
    S3_BUCKET,
    SQS_QUEUE_URL,
    DYNAMO_TABLE,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

table = dynamodb.Table(DYNAMO_TABLE)


def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    file = request.files.get("image")
    album = (request.form.get("album") or "default").strip()
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not file or file.filename == "":
        return jsonify({"error": "no file provided"}), 400
    if not allowed(file.filename):
        return jsonify({"error": "file type not allowed"}), 400

    image_id = str(uuid.uuid4())
    ext = file.filename.rsplit(".", 1)[1].lower()
    s3_key = f"albums/{album}/{image_id}.{ext}"
    uploaded_at = datetime.now(timezone.utc).isoformat()

    s3.upload_fileobj(
        file,
        S3_BUCKET,
        s3_key,
        ExtraArgs={"ContentType": file.mimetype or "application/octet-stream"},
    )

    item = {
        "album": album,
        "image_id": image_id,
        "title": title,
        "description": description,
        "s3_bucket": S3_BUCKET,
        "s3_key": s3_key,
        "content_type": file.mimetype or "",
        "original_filename": file.filename,
        "uploaded_at": uploaded_at,
    }

    sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(item))
    table.put_item(Item=item)

    return jsonify({"status": "ok", "image_id": image_id, "s3_key": s3_key})


@app.get("/albums/<album>")
def list_album(album):
    resp = table.query(
        KeyConditionExpression="album = :a",
        ExpressionAttributeValues={":a": album},
    )
    return jsonify(resp.get("Items", []))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
