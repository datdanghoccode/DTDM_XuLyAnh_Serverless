# -*- coding: utf-8 -*-
"""
web2_live_lab/pipeline_engine.py
Core Serverless Image Processing Engine integrating Mock AWS services,
SHA-256 Idempotency Lock, Pillow Resizing, and SQS DLQ Fault Isolation.
"""

import io
import time
import base64
import hashlib
from PIL import Image, UnidentifiedImageError

from shared_core.mock_aws import (
    MockS3,
    MockDynamoDB,
    MockSQS,
    ConditionalCheckFailedException
)
from shared_core.benchmark_data import BenchmarkEngine

class ServerlessPipelineEngine:
    def __init__(self):
        self.s3 = MockS3()
        self.db = MockDynamoDB()
        self.sqs = MockSQS()
        self.benchmark = BenchmarkEngine()
        self.raw_bucket = "cloud-image-raw-input"
        self.thumb_bucket = "cloud-image-thumbnails-output"
        self.metadata_table = "ImageMetadata"
        self.queue_name = "image-event-queue"
        self.dlq_name = "image-dlq"
        self.processed_count = 0

    def compute_sha256(self, file_bytes: bytes) -> str:
        """Computes cryptographic SHA-256 digest directly from binary byte stream."""
        return hashlib.sha256(file_bytes).hexdigest()

    def process_image(self, file_bytes: bytes, filename: str, is_cold: bool = False) -> dict:
        """
        Executes end-to-end pipeline:
        1. S3 Input Put
        2. Compute SHA-256
        3. DynamoDB Atomic Idempotency Lock (attribute_not_exists)
        4. Pillow Resize to 300x300 JPEG
        5. S3 Thumbnails Put & DynamoDB update to COMPLETED
        """
        start_time = time.perf_counter()

        # Step 1: Upload to Input S3
        self.s3.put_object(self.raw_bucket, filename, file_bytes)

        # Step 2: Compute SHA-256
        img_hash = self.compute_sha256(file_bytes)

        # Step 3: DynamoDB Atomic Lock
        init_item = {
            "image_hash": img_hash,
            "filename": filename,
            "status": "PROCESSING",
            "size_kb": round(len(file_bytes) / 1024.0, 2),
            "timestamp": time.time()
        }
        try:
            self.db.put_item(
                self.metadata_table,
                init_item,
                condition="attribute_not_exists(image_hash) OR status = FAILED"
            )
        except ConditionalCheckFailedException:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "SKIPPED_IDEMPOTENT",
                "hash": img_hash,
                "latency_ms": elapsed_ms,
                "reason": "ConditionalCheckFailedException: Hash already processed",
                "message": f"Ảnh đã tồn tại mã băm {img_hash[:12]}... Từ chối xử lý lặp lại."
            }

        # Step 4: Pillow Resize & Metadata extraction in RAM (io.BytesIO)
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()  # Verify image integrity

            # Re-open for actual processing (verify closes header)
            with Image.open(io.BytesIO(file_bytes)) as img:
                orig_width, orig_height = img.size
                orig_format = img.format or "JPEG"
                orig_mode = img.mode

                # Convert RGBA to RGB for JPEG compatibility
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Thumbnail resize 300x300 preserving aspect ratio
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumb_width, thumb_height = img.size

                out_buf = io.BytesIO()
                img.save(out_buf, format="JPEG", quality=85, optimize=True)
                thumb_bytes = out_buf.getvalue()

        except Exception as err:
            self.db.update_item_status(self.metadata_table, img_hash, "FAILED", {"error": str(err)})
            raise err

        # Step 5: Save to S3 Thumbnails & Update DynamoDB
        thumb_key = f"thumb_{filename.rsplit('.', 1)[0]}.jpg"
        self.s3.put_object(self.thumb_bucket, thumb_key, thumb_bytes)

        orig_kb = round(len(file_bytes) / 1024.0, 2)
        thumb_kb = round(len(thumb_bytes) / 1024.0, 2)
        compression = round(((orig_kb - thumb_kb) / orig_kb) * 100.0, 1) if orig_kb > 0 else 0.0

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        if is_cold:
            elapsed_ms += 495.0  # Add empirical Firecracker init latency

        metadata = {
            "image_hash": img_hash,
            "hash": img_hash,
            "filename": filename,
            "thumb_key": thumb_key,
            "orig_size": f"{orig_width}x{orig_height}",
            "thumb_size": f"{thumb_width}x{thumb_height}",
            "orig_kb": orig_kb,
            "thumb_kb": thumb_kb,
            "compression_percent": compression,
            "orig_format": orig_format,
            "latency_ms": elapsed_ms,
            "is_cold": is_cold,
            "status": "PROCESSED"
        }
        self.db.update_item_status(self.metadata_table, img_hash, "COMPLETED", metadata)
        self.processed_count += 1

        thumb_b64 = base64.b64encode(thumb_bytes).decode("utf-8")
        metadata["thumbnail_base64"] = f"data:image/jpeg;base64,{thumb_b64}"
        return metadata

    def simulate_duplicate(self, image_hash: str) -> dict:
        """Simulates an At-least-once network retry sending the exact same image hash."""
        start = time.perf_counter()
        item = {
            "image_hash": image_hash,
            "status": "PROCESSING",
            "timestamp": time.time()
        }
        try:
            self.db.put_item(
                self.metadata_table,
                item,
                condition="attribute_not_exists(image_hash) OR status = FAILED"
            )
            return {"status": "UNEXPECTED_WRITE", "latency_ms": 0.0}
        except ConditionalCheckFailedException:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "SKIPPED_IDEMPOTENT",
                "hash": image_hash,
                "latency_ms": max(elapsed_ms, 1.8),
                "reason": "ConditionalCheckFailedException: Hash already processed",
                "message": f"Khóa nguyên tử DynamoDB phát hiện trùng mã băm. Từ chối xử lý trong {max(elapsed_ms, 1.8)} ms."
            }

    def simulate_poison_pill(self, poison_type: str = "corrupt_bytes", filename: str = "poison_payload.jpg") -> dict:
        """Simulates corrupted/malicious file upload triggering 3 retries and SQS DLQ routing."""
        start = time.perf_counter()
        corrupt_bytes = b"NOT_AN_IMAGE_HEADER_MALICIOUS_EXE_BYTES_RANDOM_DATA_xyz"
        img_hash = self.compute_sha256(corrupt_bytes)

        # Simulate 3 retries with backoff
        retries = 3
        retry_logs = []
        for r in range(1, retries + 1):
            retry_logs.append({
                "attempt": r,
                "backoff_ms": 50 * (2 ** (r - 1)),
                "exception": "UnidentifiedImageError: cannot identify image file"
            })

        # Put into DLQ after retries exhausted
        dlq_payload = {
            "image_hash": img_hash,
            "filename": filename,
            "poison_type": poison_type,
            "error": "UnidentifiedImageError: cannot identify image file (corrupted magic bytes)",
            "retries_attempted": 3,
            "quarantined_at": time.time(),
            "retention_days": 14
        }
        msg_id = self.sqs.send_message(self.dlq_name, dlq_payload)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "status": "ROUTED_TO_DLQ",
            "message_id": msg_id,
            "hash": img_hash,
            "filename": filename,
            "error": "UnidentifiedImageError: cannot identify image file",
            "retries_attempted": 3,
            "retry_logs": retry_logs,
            "dlq_name": self.dlq_name,
            "latency_ms": elapsed_ms,
            "message": f"Tệp hỏng đã retry 3 lần thất bại và được cô lập an toàn vào {self.dlq_name}."
        }
