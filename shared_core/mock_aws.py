# -*- coding: utf-8 -*-
"""
shared_core/mock_aws.py
In-Memory High-Fidelity Simulation of AWS Services (S3, DynamoDB, SQS).
Provides exact atomic semantics for Conditional Puts and FIFO/DLQ message routing.
"""

import threading
import time
import uuid

class ConditionalCheckFailedException(Exception):
    """Raised when DynamoDB condition expression evaluation fails."""
    pass

class MockS3:
    """In-memory thread-safe simulation of Amazon S3."""
    def __init__(self):
        self._lock = threading.Lock()
        self._buckets = {}

    def put_object(self, bucket: str, key: str, data: bytes) -> dict:
        with self._lock:
            if bucket not in self._buckets:
                self._buckets[bucket] = {}
            self._buckets[bucket][key] = {
                "data": data,
                "size": len(data),
                "created_at": time.time(),
                "etag": str(uuid.uuid4()).replace("-", "")[:32]
            }
            return {
                "Bucket": bucket,
                "Key": key,
                "ETag": self._buckets[bucket][key]["etag"],
                "Size": len(data)
            }

    def get_object(self, bucket: str, key: str) -> bytes:
        with self._lock:
            if bucket not in self._buckets or key not in self._buckets[bucket]:
                raise KeyError(f"NoSuchKey: The specified key '{key}' does not exist in bucket '{bucket}'.")
            return self._buckets[bucket][key]["data"]

    def object_exists(self, bucket: str, key: str) -> bool:
        with self._lock:
            return bucket in self._buckets and key in self._buckets[bucket]

    def delete_object(self, bucket: str, key: str) -> bool:
        with self._lock:
            if bucket in self._buckets and key in self._buckets[bucket]:
                del self._buckets[bucket][key]
                return True
            return False

    def list_objects(self, bucket: str) -> list:
        with self._lock:
            if bucket not in self._buckets:
                return []
            return [
                {"Key": k, "Size": v["size"], "CreatedAt": v["created_at"]}
                for k, v in self._buckets[bucket].items()
            ]

class MockDynamoDB:
    """In-memory thread-safe simulation of Amazon DynamoDB with atomic condition evaluation."""
    def __init__(self):
        self._lock = threading.Lock()
        self._tables = {}

    def put_item(self, table: str, item: dict, condition: str = None) -> bool:
        with self._lock:
            if table not in self._tables:
                self._tables[table] = {}

            # Primary key convention for ImageMetadata is 'image_hash'
            pk = item.get("image_hash")
            if not pk:
                raise ValueError("Item missing required primary key 'image_hash'")

            # Condition evaluation
            if condition:
                cond_clean = condition.strip().lower()
                if "attribute_not_exists(image_hash)" in cond_clean:
                    if pk in self._tables[table]:
                        existing = self._tables[table][pk]
                        # Allow retry if previous attempt strictly FAILED
                        if "status = failed" in cond_clean:
                            if existing.get("status") != "FAILED":
                                raise ConditionalCheckFailedException(
                                    f"ConditionalCheckFailed: Item with image_hash '{pk}' already exists with status '{existing.get('status')}'"
                                )
                        else:
                            raise ConditionalCheckFailedException(
                                f"ConditionalCheckFailed: Item with image_hash '{pk}' already exists."
                            )

            # Atomic write
            item_copy = dict(item)
            item_copy["_updated_at"] = time.time()
            self._tables[table][pk] = item_copy
            return True

    def get_item(self, table: str, key_dict: dict) -> dict:
        with self._lock:
            if table not in self._tables:
                return {}
            pk = key_dict.get("image_hash")
            return dict(self._tables[table].get(pk, {}))

    def update_item_status(self, table: str, image_hash: str, status: str, extra: dict = None) -> bool:
        with self._lock:
            if table not in self._tables or image_hash not in self._tables[table]:
                return False
            self._tables[table][image_hash]["status"] = status
            self._tables[table][image_hash]["_updated_at"] = time.time()
            if extra:
                self._tables[table][image_hash].update(extra)
            return True

    def scan(self, table: str) -> list:
        with self._lock:
            if table not in self._tables:
                return []
            return [dict(v) for v in self._tables[table].values()]

class MockSQS:
    """In-memory thread-safe simulation of Amazon SQS with DLQ isolation and Redrive."""
    def __init__(self):
        self._lock = threading.Lock()
        self._queues = {}

    def send_message(self, queue: str, body: dict) -> str:
        with self._lock:
            if queue not in self._queues:
                self._queues[queue] = []
            msg_id = str(uuid.uuid4())
            msg = {
                "id": msg_id,
                "body": body,
                "timestamp": time.time(),
                "receipt_handle": f"rcpt_{msg_id}"
            }
            self._queues[queue].append(msg)
            return msg_id

    def receive_messages(self, queue: str, max_msgs: int = 10) -> list:
        with self._lock:
            if queue not in self._queues:
                return []
            return [dict(m) for m in self._queues[queue][:max_msgs]]

    def delete_message(self, queue: str, receipt_handle: str) -> bool:
        with self._lock:
            if queue not in self._queues:
                return False
            initial_len = len(self._queues[queue])
            self._queues[queue] = [m for m in self._queues[queue] if m["receipt_handle"] != receipt_handle]
            return len(self._queues[queue]) < initial_len

    def redrive_dlq(self, src_dlq: str, dest_queue: str) -> int:
        """Pumps all messages from DLQ back into the main destination queue."""
        with self._lock:
            if src_dlq not in self._queues:
                return 0
            if dest_queue not in self._queues:
                self._queues[dest_queue] = []

            messages_to_move = list(self._queues[src_dlq])
            self._queues[src_dlq] = []
            
            for m in messages_to_move:
                m["receipt_handle"] = f"rcpt_redrive_{uuid.uuid4()}"
                m["redriven_at"] = time.time()
                self._queues[dest_queue].append(m)

            return len(messages_to_move)

    def get_queue_depth(self, queue: str) -> int:
        with self._lock:
            return len(self._queues.get(queue, []))
