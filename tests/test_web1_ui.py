# -*- coding: utf-8 -*-
"""
tests/test_web1_ui.py
Tests verifying Web 1 template structure, 7 academic modules, and static assets.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from web1_learning_hub.app import create_app

class TestWeb1UI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_web1_index_template_renders_all_modules(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Verify all 7 modules exist in the document
        self.assertIn("module-1", html)
        self.assertIn("module-2", html)
        self.assertIn("module-3", html)
        self.assertIn("module-4", html)
        self.assertIn("module-5", html)
        self.assertIn("module-6", html)
        self.assertIn("module-7", html)

        # Verify key academic terms from syllabus
        self.assertIn("Câu hỏi nghiên cứu", html)
        self.assertIn("Cold Start", html)
        self.assertIn("Idempotency", html)
        self.assertIn("OWASP Serverless", html)
        self.assertIn("512MB", html)
        self.assertIn("Live Lab", html)

    def test_web1_static_assets_exist(self):
        css_path = os.path.join(os.path.dirname(__file__), "..", "web1_learning_hub", "static", "css", "style.css")
        js_path = os.path.join(os.path.dirname(__file__), "..", "web1_learning_hub", "static", "js", "walkthrough.js")
        self.assertTrue(os.path.exists(css_path), "Web 1 style.css must exist")
        self.assertTrue(os.path.exists(js_path), "Web 1 walkthrough.js must exist")

if __name__ == "__main__":
    unittest.main()
