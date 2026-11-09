import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('policy_gate',ROOT/'scripts/policy_gate.py')
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
POLICY=json.loads((ROOT/'ops_policy.json').read_text(encoding='utf-8'))

class SafetyGateTests(unittest.TestCase):
    def test_valid_game_edit(self):
        self.assertEqual(p.validate_changes([dict(path='games/emotion-garden/index.html',size=5,content=b'hello')],POLICY),[])
    def test_rejects_ci_edit(self):
        self.assertTrue(p.validate_changes([dict(path='.github/workflows/quality.yml',size=1,content=b'1')],POLICY))
    def test_rejects_traversal(self):
        self.assertTrue(p.validate_changes([dict(path='games/../../secrets.txt',size=1,content=b'1')],POLICY))
    def test_rejects_secret(self):
        self.assertTrue(p.validate_changes([dict(path='games/a.js',size=45,content=b'const k="sk-abcdefghijklmnopqrstuvwxyz012345"')],POLICY))
    def test_rejects_external_script(self):
        self.assertTrue(p.validate_changes([dict(path='games/a.html',size=50,content=b'<script src="https://example.com/x.js"></script>')],POLICY))
    def test_rejects_symlink(self):
        self.assertTrue(p.validate_changes([dict(path='docs/file.md',size=0,content=b'',is_symlink=True)],POLICY))
    def test_rejects_empty_patch(self):
        self.assertTrue(p.validate_changes([],POLICY))
    def test_rejects_large_file(self):
        self.assertTrue(p.validate_changes([dict(path='tests/a.py',size=210000,content=b'x')],POLICY))

if __name__=='__main__': unittest.main()
