# -*- coding: utf-8 -*-
"""
tests/test_e2e_launch.py
Tests verifying the master launcher script (run_project.py) and 1-click batch script (run_all.bat).
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

class TestMasterLauncher(unittest.TestCase):
    def test_run_project_file_and_components(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        launcher_path = os.path.join(root_dir, "run_project.py")
        self.assertTrue(os.path.exists(launcher_path), "run_project.py must exist in root workspace")

        # Import run_project components
        import run_project
        self.assertTrue(hasattr(run_project, "check_port_available"), "run_project must have check_port_available helper")
        self.assertTrue(hasattr(run_project, "start_servers"), "run_project must have start_servers helper")

        # Verify that both apps can be instantiated by launcher
        web1 = run_project.get_web1_app()
        web2 = run_project.get_web2_app()

        with web1.test_client() as c1:
            res1 = c1.get("/api/health")
            self.assertEqual(res1.status_code, 200)
            data1 = res1.get_json()
            self.assertEqual(data1.get("status"), "ok")

        with web2.test_client() as c2:
            res2 = c2.get("/api/status")
            self.assertEqual(res2.status_code, 200)
            data2 = res2.get_json()
            self.assertEqual(data2.get("status"), "ok")

    def test_run_all_bat_file_exists_and_contains_commands(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        bat_path = os.path.join(root_dir, "run_all.bat")
        self.assertTrue(os.path.exists(bat_path), "run_all.bat must exist in root workspace")

        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("python run_project.py", content, "run_all.bat must invoke python run_project.py")
        self.assertIn("flask", content.lower(), "run_all.bat should check or install flask")

if __name__ == "__main__":
    unittest.main()
