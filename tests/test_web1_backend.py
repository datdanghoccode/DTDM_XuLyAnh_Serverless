# -*- coding: utf-8 -*-
"""
tests/test_web1_backend.py
Tests verifying Web 1 Knowledge & Learning Hub backend routes and Code API.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from web1_learning_hub.app import create_app

class TestWeb1Backend(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_web1_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["app"], "web1_learning_hub")
        self.assertEqual(data["port"], 5001)

    def test_web1_code_snippet_api(self):
        # 1. Test Idempotency snippet
        res = self.client.get("/api/code/idempotency_lock")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("attribute_not_exists", data["code"])
        self.assertEqual(data["title"], "Khóa Lũy Đẳng Nguyên Tử DynamoDB")
        self.assertTrue(len(data["highlights"]) > 0)

        # 2. Test IAM snippet
        res_iam = self.client.get("/api/code/iam_least_privilege")
        self.assertEqual(res_iam.status_code, 200)
        data_iam = res_iam.get_json()
        self.assertIn("aws_iam_policy", data_iam["code"])

        # 3. Test Poison Pill SQS DLQ snippet
        res_dlq = self.client.get("/api/code/sqs_dlq_redrive")
        self.assertEqual(res_dlq.status_code, 200)
        data_dlq = res_dlq.get_json()
        self.assertIn("maxReceiveCount", data_dlq["code"])

if __name__ == "__main__":
    unittest.main()
