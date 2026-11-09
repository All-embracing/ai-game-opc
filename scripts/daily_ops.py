#!/usr/bin/env python3
"""Repeatable daily operating brief; stdlib only. No fake AI or external analytics."""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def pick_task(tasks):
    queue = [t for t in tasks if t.get('status') == 'todo']
    return min(queue, key=lambda t: (int(t['priority']), t['id'])) if queue else None

def calculate_gate(row, goal):
    if not row or not row.get('playtests') or int(float(row['playtests'])) < goal['playtests']:
        return '等待样本：尚未完成至少 %d 名玩家的试玩，不对商业潜力作结论。' % goal['playtests']
    issues=[]
    for k,label in [('first_round_completion_pct','首局完成率'),('want_replay_pct','愿意再玩比例')]:
        if float(row[k]) < goal[k]:
            issues.append(label)
    if float(row['bugs_open']) > goal['max_blocker_bugs']:
        issues.append('未解决严重缺陷数（请确保 bugs_open 仅填写阻断级）')
    return '进入下一开发阶段：全部验收条件达到阈值，但仍需人工审核。' if not issues else '暂缓进入下一阶段；待改善：'+'、'.join(issues)+'。'

def make_report(config,tasks,metrics,now=None):
    now=now or datetime.now(ZoneInfo(config['timezone']))
    latest=metrics[-1] if metrics else None
    top=pick_task(tasks)
    monthly = [m for m in metrics if m.get('date','')[:7] == now.strftime('%Y-%m')]
    spent=sum(float(m['spend_cny'] or 0) for m in monthly)
    earned=sum(float(m['revenue_cny'] or 0) for m in monthly)
    sections=[f"# OPC 游戏工作室每日作战报告 · {now:%Y-%m-%d}",
              f"**阶段**：{config['phase']} · **产品**：{config['first_game']}",
              "## 第一优先任务"]
    if top:
        sections.extend([f"**{top['id']} · {top['title']}**",f"负责人：{top['owner']}；验收：{top['acceptance']}"])
    else:
        sections.append('当前任务队列已清空，请人工确认下一阶段目标。')
    sections.append('## 验收门槛判断')
    sections.append(calculate_gate(latest,config['phase_gate']))
    sections.append('## 最近一条手工录入指标')
    if latest:
        sections.append(' | '.join(f'{key}: {val}' for key,val in latest.items()))
        sections.append('注意：仅使用录入的真实数据；缺失数据不得视为零收入或零留存的事实。')
    else:
        sections.append('尚无指标。请填入实际测试数据。')
    if monthly:
        sections.extend(['## 本月现金流（仅基于本月已录入的记录）',f'已录入支出：¥{spent:.2f}；已录入收入：¥{earned:.2f}；净额：¥{earned-spent:.2f}。',f'内部预算上限：¥{config["monthly_operating_cap_cny"]}；按已录入数据推算剩余额度：¥{config["monthly_operating_cap_cny"]-spent:.2f}（不含未录入支出）。'])
    else:
        sections.extend(['## 本月现金流（真实数据待录入）',f'尚无本月真实财务记录，不能据此认定支出、收入或利润为 0。内部预算上限（规划值）：¥{config["monthly_operating_cap_cny"]}。'])
    sections.extend(['## 审批提醒','支出、正式发布、授权/IP、玩家正式沟通、真实数据修改和定价变更须由负责人审批。', '## 每日反馈格式','已完成：___；证据链接：___；阻塞：___；下一任务：___。'])
    return '\n\n'.join(sections)+'\n'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stdout', action='store_true', help='Print report (also writes reports/)')
    args=p.parse_args()
    config=json.loads((ROOT/'studio.json').read_text(encoding='utf-8'))
    tasks=json.loads((ROOT/'data/backlog.json').read_text(encoding='utf-8'))
    metrics=read_csv(ROOT/'data/metrics.csv')
    now=datetime.now(ZoneInfo(config['timezone']))
    report=make_report(config,tasks,metrics,now)
    dest=ROOT/'reports'/f'{now:%Y-%m-%d}.md'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(report,encoding='utf-8')
    print(report if args.stdout else 'Generated: '+str(dest))

if __name__=='__main__':main()
