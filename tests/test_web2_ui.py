# -*- coding: utf-8 -*-
"""
tests/test_web2_ui.py
Tests verifying Web 2 Live Lab template rendering, UI sections, and asset existence.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from web2_live_lab.app import create_app

class TestWeb2UI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_web2_index_route_renders_successfully(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        
        # Verify title and branding
        self.assertIn("Học viện & Phòng Thí nghiệm Serverless", html)
        self.assertIn("Visual Pipeline Canvas", html)
        
        # Verify all 4 tabs exist
        self.assertIn("tab-standard", html)
        self.assertIn("tab-idempotent", html)
        self.assertIn("tab-poison", html)
        self.assertIn("tab-benchmark", html)
        
        # Verify DLQ and Telemetry sections
        self.assertIn("console-terminal", html)
        self.assertIn("dlq-modal", html)

    def test_static_assets_exist(self):
        css_path = os.path.join(os.path.dirname(__file__), "..", "web2_live_lab", "static", "css", "style.css")
        js_path = os.path.join(os.path.dirname(__file__), "..", "web2_live_lab", "static", "js", "lab.js")
        self.assertTrue(os.path.exists(css_path), "style.css must exist")
        self.assertTrue(os.path.exists(js_path), "lab.js must exist")

if __name__ == "__main__":
    unittest.main()
