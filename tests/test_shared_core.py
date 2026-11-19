# -*- coding: utf-8 -*-
"""
tests/test_shared_core.py
Unit tests for Mock AWS Services (S3, DynamoDB, SQS) and Benchmark Data Engine.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from shared_core.mock_aws import (
    MockS3,
    MockDynamoDB,
    MockSQS,
    ConditionalCheckFailedException
)
from shared_core.benchmark_data import BenchmarkEngine

class TestSharedCore(unittest.TestCase):
    def setUp(self):
        self.s3 = MockS3()
        self.db = MockDynamoDB()
        self.sqs = MockSQS()
        self.benchmark = BenchmarkEngine()

    def test_s3_upload_and_get(self):
        self.s3.put_object("raw-bucket", "sample.jpg", b"fake-jpg-binary")
        retrieved = self.s3.get_object("raw-bucket", "sample.jpg")
        self.assertEqual(retrieved, b"fake-jpg-binary")
        self.assertTrue(self.s3.object_exists("raw-bucket", "sample.jpg"))
        self.assertFalse(self.s3.object_exists("raw-bucket", "non-existent.jpg"))

    def test_dynamodb_atomic_conditional_put(self):
        item = {
            "image_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "status": "PROCESSING",
            "file_name": "photo.jpg"
        }
        # First write succeeds
        result = self.db.put_item("ImageMetadata", item, condition="attribute_not_exists(image_hash)")
        self.assertTrue(result)
        
        # Second write with exact same image_hash must raise ConditionalCheckFailedException
        with self.assertRaises(ConditionalCheckFailedException):
            self.db.put_item("ImageMetadata", item, condition="attribute_not_exists(image_hash)")

    def test_sqs_send_receive_and_dlq_redrive(self):
        # Send poisoned message to DLQ
        msg_id = self.sqs.send_message("image-dlq", {
            "error": "UnidentifiedImageError",
            "file_name": "malicious.exe.jpg",
            "retries": 3
        })
        self.assertTrue(len(msg_id) > 0)
        
        # Verify message in DLQ
        dlq_msgs = self.sqs.receive_messages("image-dlq", max_msgs=10)
        self.assertEqual(len(dlq_msgs), 1)
        self.assertEqual(dlq_msgs[0]["body"]["file_name"], "malicious.exe.jpg")
        
        # Test redrive from DLQ to main queue
        redriven_count = self.sqs.redrive_dlq("image-dlq", "image-queue")
        self.assertEqual(redriven_count, 1)
        self.assertEqual(len(self.sqs.receive_messages("image-dlq")), 0)
        
        main_msgs = self.sqs.receive_messages("image-queue")
        self.assertEqual(len(main_msgs), 1)

    def test_benchmark_percentile_calculation(self):
        durations = [25.0, 26.5, 27.0, 30.0, 35.0, 50.0, 100.0, 250.0, 500.0, 1000.0]
        percentiles = self.benchmark.calculate_percentiles(durations)
        self.assertIn("p50", percentiles)
        self.assertIn("p90", percentiles)
        self.assertIn("p95", percentiles)
        self.assertIn("p99", percentiles)
        self.assertLessEqual(percentiles["p50"], percentiles["p95"])

    def test_benchmark_verified_dataset_matches_course_specs(self):
        dataset = self.benchmark.get_verified_dataset()
        self.assertEqual(len(dataset), 100)
        
        warm_runs = [r for r in dataset if r.get("is_cold") is False and r.get("status") in ["SUCCESS", "COMPLETED"]]
        cold_runs = [r for r in dataset if r.get("is_cold") is True]
        self.assertGreater(len(warm_runs), 75)
        self.assertGreater(len(cold_runs), 3)

if __name__ == "__main__":
    unittest.main()
