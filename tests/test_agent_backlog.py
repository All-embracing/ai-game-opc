"""Safety checks for the explicitly allowlisted AI development queue."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class AgentBacklogTest(unittest.TestCase):
    def test_agent_task_is_explicitly_allowlisted(self):
        tasks = json.loads((ROOT / 'data' / 'backlog.json').read_text(encoding='utf-8'))
        eligible = [t for t in tasks if t.get('agent_eligible') is True and t.get('status') == 'todo']
        self.assertGreater(len(eligible), 0, 'Must explicitly allow at least one safe automation task.')
        self.assertTrue(all(t.get('owner') in ('Dev','Data') for t in eligible))

    def test_human_approval_work_never_eligible(self):
        tasks = json.loads((ROOT / 'data' / 'backlog.json').read_text(encoding='utf-8'))
        human = {'G-001','G-003','G-004','G-006'}
        by_id = {t['id']: t for t in tasks}
        for task_id in human:
            self.assertFalse(by_id[task_id].get('agent_eligible'), task_id)

if __name__ == '__main__':
    unittest.main()
