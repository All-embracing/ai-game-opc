# AI 游戏 OPC：研发与运营起步工程 v0.3

> 目标：1 位负责人 + AI 开发流程 + 自动化质量门禁 + 数据驱动的游戏产品运营。
> **状态：玩法概念与运营基础设施的可运行样板；未具备正式商业上线能力。**

## 即刻体验

新用户请先阅读 `START_HERE.md`。Windows 用户可执行 `powershell -ExecutionPolicy Bypass -File scripts/quickstart.ps1` 做本地测试与离线部署检查。

1. 直接用浏览器打开 `games/emotion-garden/index.html`，试玩《七灵·心隅花园》核心消除循环。也可在根目录运行 `python -m http.server 8000` 后打开 `http://localhost:8000/games/emotion-garden/`。
2. 在根目录执行 `python -m unittest discover -s tests -v`，运行自动测试。
3. 执行 `python scripts/daily_ops.py`，生成 `reports/YYYY-MM-DD.md` 每日作战报告。
4. 修改 `data/backlog.json`（任务）、`data/metrics.csv`（只录真实指标）、`studio.json`（运营设置），再生成日报。
5. 将工程推送至自己的 GitHub 私有仓库。启用 Actions 后，`quality.yml` 在推送时运行测试；`daily-brief.yml` 每天按 UTC 00:00 尝试自动生成/更新一个固定 GitHub Issue，并上传日报供下载。GitHub 计划任务可能延迟或因仓库不活跃被停用；不保证精确到秒。

## 已实现

- 浏览器可玩的本地玩法原型：6×6 四种心情光点，点击相邻同色群，18 步目标制，关卡递进，3 位精灵能力区别，花园进度存储。
- 数据源驱动的每日任务优先级、验收门槛判断、现金流摘要（注意缺失数据不会自动补全）。
- 零额外包依赖的 Python 日报脚本、自动化单元测试、持续集成配置。
- 只维护一个 GitHub 日报 Issue，避免每天创建海量重复任务。

## 尚未实现

完整视觉资产、正式游戏设计稿、美术资产权利核验、Steam SDK、账号后端、数据采集/用户同意、变现、国内上线资质、云端 AI 自主编程、自主 PR/代码审查、自动商店发布等。

*不要把“定时生成报告”误解为 AI 已持续开发游戏；要做到每日自动写代码，需再部署持久化 AI 开发执行器、权限隔离和 PR 审批。*

## 推荐管理纪律

- 一天只确定一项必须完成的优先任务；WIP 不超过 2。
- 每个任务必须有可复核验收标准和证据链接。
- 无人工明确批准，不允许 AI 付款、发布生产版本、修改账款、对外做版权承诺。
- 游戏项目的源码、资产、账号、代码仓库必须属于公司主体或获得明确使用授权。

## 目录

```text
README.md
studio.json
.github/workflows/daily-brief.yml   # 每日运营面板
.github/workflows/quality.yml       # 自动测试
scripts/daily_ops.py              # 每日流程
scripts/check_placeholder.md      # 扩展预留说明
tests/test_daily_ops.py           # 基础测试
data/backlog.json                 # 工作队列
data/metrics.csv                  # 测试数据
data/decisions.csv                # 决策记录
games/emotion-garden/index.html   # 本地可玩原型
docs/                             # 商业和实施说明
```

## v0.2：GitHub + Codex 自动开发候选工作流

本包新增 `.github/workflows/ai-daily-dev.yml`、`AGENTS.md`、`docs/AI_AGENT_TASK.md`、`.gitignore` 与额外安全测试。开始前，请阅读 `docs/04-github-and-ai-executor-guide.md`。自动开发每天**默认关闭**，手动执行并通过验收后，才在 GitHub 仓库 Variables 里设置 `ENABLE_AUTONOMOUS_CODING=true`。

**说明：** 这个流程会在 GitHub 的临时执行器中生成、验证和提交代码候选 PR；不会自动合并，也不是已投入运行的全天候云服务器。你需要自行创建私有仓库、配置 API Secret、允许 GitHub Actions 创建 Pull Request。此包仍不包含真正持久在线 VPS 的部署程序。

## v0.3：运维安全与部署自检（本版新增）

- `scripts/policy_gate.py`：在独立验证 job 中校验 AI 补丁，仅允许 `games/`、`tests/`、`docs/` 改动；拦截删除、符号链接、明显密钥、远程 JS 加载和过大文件。**不能替代人工安全评审**。
- `scripts/doctor.py`：只读检查工程结构、任务队列、数据真实性提示和 GitHub origin 是否存在；明确不能证明云端已连接。
- `ops_policy.json`：AI 可写范围和敏感审批操作配置。
- `data/asset-register.csv`、`data/experiments.csv`、`data/risk-register.csv`：商业素材授权、玩家实验、经营风险的基本台账。
- `data/metrics.csv` 只留表头，不再附带虚构的全零数据行；无数据的财务报告明确标注“未知”。
- `docs/05-OPC-execution-playbook.md`：账户、权限、运行和验收手册。
- `docs/06-OPC-gap-and-delegation.md`：自动化责任边界和上线前缺口。

首次检查：`python -m unittest discover -s tests -v`；`python scripts/doctor.py`。

**实际状态**：本地通过测试 != GitHub 已连接，也 != AI 已在云端连续运行。要实现真正每天写代码，仍须完成用户侧账号授权、API 费用控制、仓库上传与首次 GitHub Actions 云端测试。
