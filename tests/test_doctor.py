import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('doctor',ROOT/'scripts/doctor.py')
doc=importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc)

class DoctorTests(unittest.TestCase):
    def test_offline_cannot_claim_deployment(self):
        result={x['check']:x for x in doc.check_project(ROOT)}
        self.assertFalse(result['cloud_actions_verified']['pass'])
        self.assertFalse(result['api_credentials_verified']['pass'])
        self.assertTrue(result['project_structure']['pass'])
    def test_metrics_schema(self):
        result={x['check']:x for x in doc.check_project(ROOT)}
        self.assertTrue(result['metrics_schema']['pass'])

if __name__=='__main__': unittest.main()
