import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from scripts.daily_ops import pick_task, calculate_gate, make_report

class DailyOpsTest(unittest.TestCase):
    def test_priority(self):
        tasks=[{'id':'2','title':'b','priority':2,'status':'todo'},{'id':'1','title':'a','priority':1,'status':'todo'}]
        self.assertEqual(pick_task(tasks)['id'],'1')
    def test_requires_sample(self):
        self.assertIn('等待样本',calculate_gate({'playtests':'3'}, {'playtests':15}))
    def test_pass(self):
        row={'playtests':'18','first_round_completion_pct':'85','want_replay_pct':'66','bugs_open':'0'}
        goal={'playtests':15,'first_round_completion_pct':70,'want_replay_pct':50,'max_blocker_bugs':0}
        self.assertIn('进入下一开发阶段',calculate_gate(row,goal))
    def test_fail(self):
        row={'playtests':'18','first_round_completion_pct':'30','want_replay_pct':'66','bugs_open':'0'}
        goal={'playtests':15,'first_round_completion_pct':70,'want_replay_pct':50,'max_blocker_bugs':0}
        self.assertIn('首局完成率',calculate_gate(row,goal))
    def test_report(self):
        cfg={'timezone':'Asia/Shanghai','phase':'test','first_game':'Garden','phase_gate':{'playtests':15},'monthly_operating_cap_cny':5000}
        tasks=[{'id':'001','title':'Try','priority':1,'status':'todo','owner':'QA','acceptance':'15 users'}]
        rows=[{'date':'2026-11-09','playtests':'0','first_round_completion_pct':'0','want_replay_pct':'0','avg_session_minutes':'0','bugs_open':'0','spend_cny':'100','revenue_cny':'0'}]
        now=datetime(2026,11,9,9,0,tzinfo=ZoneInfo('Asia/Shanghai'))
        result=make_report(cfg,tasks,rows,now)
        self.assertIn('¥100.00',result)
        self.assertIn('Try',result)

if __name__ == '__main__':unittest.main()
