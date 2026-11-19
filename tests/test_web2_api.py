# -*- coding: utf-8 -*-
"""
tests/test_web2_api.py
Integration tests for Web 2 Live Lab REST APIs (:5002).
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import unittest
from PIL import Image
from web2_live_lab.app import create_app

class TestWeb2Api(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_api_status(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("live"))
        self.assertIn("processed_count", data)

    def test_api_upload_valid_image(self):
        # Generate valid test image
        buf = io.BytesIO()
        img = Image.new("RGB", (640, 480), color=(56, 189, 248))
        img.save(buf, format="JPEG")
        buf.seek(0)

        res = self.client.post(
            "/api/upload",
            data={"image": (buf, "test_landscape.jpg")},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "PROCESSED")
        self.assertIn("hash", data)
        self.assertIn("thumbnail_base64", data)
        self.assertIn("latency_ms", data)
        self.assertGreater(data["compression_percent"], 50.0)

    def test_api_idempotent_duplicate_detection(self):
        # 1. Upload first image
        buf = io.BytesIO()
        img = Image.new("RGB", (300, 300), color=(16, 185, 129))
        img.save(buf, format="PNG")
        buf.seek(0)

        res1 = self.client.post(
            "/api/upload",
            data={"image": (buf, "duplicate_candidate.png")},
            content_type="multipart/form-data"
        )
        self.assertEqual(res1.status_code, 200)
        img_hash = res1.get_json()["hash"]

        # 2. Re-send duplicate hash
        res2 = self.client.post("/api/simulate-duplicate", json={"image_hash": img_hash})
        self.assertEqual(res2.status_code, 200)
        data = res2.get_json()
        self.assertEqual(data["status"], "SKIPPED_IDEMPOTENT")
        self.assertLess(data["latency_ms"], 15.0)  # Must be fast (<15ms, locally ~2ms)
        self.assertEqual(data["reason"], "ConditionalCheckFailedException: Hash already processed")

    def test_api_poison_pill_routed_to_dlq(self):
        res = self.client.post("/api/simulate-poison", json={
            "poison_type": "corrupt_magic_bytes",
            "filename": "fake_malware.exe.jpg"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ROUTED_TO_DLQ")
        self.assertEqual(data["retries_attempted"], 3)
        self.assertIn("UnidentifiedImageError", data["error"])

        # Check DLQ messages endpoint
        dlq_res = self.client.get("/api/dlq")
        self.assertEqual(dlq_res.status_code, 200)
        messages = dlq_res.get_json()["messages"]
        self.assertGreaterEqual(len(messages), 1)

    def test_api_benchmark_verified_dataset(self):
        res = self.client.get("/api/benchmark?mode=verified")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data["runs"]), 100)
        self.assertIn("percentiles", data)
        self.assertIn("p50", data["percentiles"])
        self.assertIn("p95", data["percentiles"])
        self.assertEqual(data["error_rate"], 0.0)

if __name__ == "__main__":
    unittest.main()
