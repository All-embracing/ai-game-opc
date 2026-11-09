# AI 游戏 OPC — GitHub + 云端 AI 执行环境接入指南（v0.2，历史说明）

> 最新操作和安全检查以 `docs/05-OPC-execution-playbook.md`（V0.3）为准。

> **真实状态：** 本仓库已具备可上传的 GitHub Actions 配置与 Codex 自动提交候选 PR 流程，但尚未连接你的 GitHub 账号，也尚未实际在你的 GitHub Actions 账户内运行。

## 方案 A：先用 GitHub 托管运行器（推荐）

### 第一步：创建私有仓库

1. 注册/登录 https://github.com
2. Windows 打开 PowerShell，安装 Git 与 GitHub CLI：
   ```powershell
   winget install --id Git.Git -e
   winget install --id GitHub.cli -e
   ```
   安装完请重新打开 PowerShell。
3. 解压本包，然后进入包含 `README.md`、`.github`、`games`、`tests` 的 **opc-game-studio** 文件夹。
4. 命令执行：
   ```powershell
   gh auth login
   git init -b main
   git add .
   git commit -m "Initialize AI Game OPC v0.2"
   gh repo create ai-game-opc --private --source=. --remote=origin --push
   ```
   如果 Git 要求设置用户名和邮箱，先用 `git config --global user.name "你的GitHub名称"` 和 `git config --global user.email "你的GitHub邮箱"` 设置。

### 第二步：连接 OpenAI API，不要公开密钥

1. 在 https://platform.openai.com/api-keys 创建 API Key。注意：ChatGPT 订阅与 API 计费分别管理。
2. GitHub 仓库 → `Settings → Secrets and variables → Actions → Secrets → New repository secret`。
3. Name 使用 `OPENAI_API_KEY`，Secret 为私密 API Key。
4. API 项目设置支出预算/报警阈值；GitHub Actions 也设置使用限制。不要把密钥放在 `.env` 并提交到 GitHub。

### 第三步：允许工作流创建待审核的 PR

1. GitHub 仓库 → `Settings → Actions → General`，确认可运行使用到的 Actions。
2. 页面底部 `Workflow permissions` 确认 `Allow GitHub Actions to create and approve pull requests` 已勾选并保存。
3. 建议将 `main` 设为需要 Pull Request 审核与状态检查的保护分支。注意：截至 2026 年 11 月，GitHub Free 对私有仓库不提供可强制执行的受保护分支 / Rulesets；通常需 GitHub Pro / Team 等支持私有仓库保护的计划。免费私有仓库也可遵循手工审查，但不等于平台强制防护。不要启用自动合并。
4. `Actions → OPC AI Daily Dev (Propose PR Only) → Run workflow`，先人工触发首轮；**这一步就会使用 API 并可能产生费用**。
5. 成功时应该看到三个阶段：`propose`、`verify`、`submit_for_review`。若没有安全改动，则不会有 PR；若测试失败则不会进入 PR 发布阶段。

### 第四步：启用每天自动开发

1. GitHub 仓库 → `Settings → Secrets and variables → Actions → Variables → New repository variable`。
2. Name: `ENABLE_AUTONOMOUS_CODING`；Value: `true`。
3. `ai-daily-dev.yml` 将在每天 UTC 01:37 **尝试启动**（约北京时间 09:37）。定时任务可能延迟，且 GitHub 托管运行器不是 24 小时持久在线环境。
4. AI 不会自动合并代码；你在 Pull requests 审核和 Merge。合并后，在 `data/backlog.json` 中更新任务状态并安排下一项可由 AI 开发的任务。

### 已有工作流

- `.github/workflows/quality.yml`：代码 push / PR 后运行项目测试；
- `.github/workflows/daily-brief.yml`：每天更新 GitHub Issue 运营面板（不调用 AI）；
- `.github/workflows/ai-daily-dev.yml`：Codex 自动提代码候选，隔离执行自动测试，只创建需要你审批的 PR。

**安全设计**：AI 工作阶段只有只读 GitHub 令牌与 Codex API 代理；生成的代码测试在不携带 API 密钥的单独 job 进行；PR job 具备有限写权限，但仅应用已经测试过的补丁且不执行游戏代码。提示词从仓库内可信文件读取，不直接执行外部 Issue 内容。

## 方案 B：真正长驻的云服务器（进阶）

GitHub Actions 是按触发条件启动、结束后销毁的工作环境。只有当任务需要连续运行、保留大量本地缓存、长期测试服务、长时间排队时才需要独立服务器。

推荐从 Linux VPS / 云主机 Ubuntu LTS 开始，按实际需求选择约 2–4 vCPU、4–8 GB 内存、40–80 GB 磁盘的起步配置（资源建议，不是报价）。设置：

- 云主机：独立非 root 用户、SSH 密钥登录、系统更新与防火墙；
- 执行环境：Docker 容器 + 持久卷 `/srv/opc/state`、`/srv/opc/logs`，每个任务有独立隔离工作目录；
- 任务调度：systemd timer / cron / 队列 Worker，从受控任务库选择工作；
- 代码仓库：通过最低权限 GitHub App 或专用凭据拉取、创建 PR；
- AI：Codex CLI 非交互模式，凭据由秘密管理服务提供、仅对调用进程可见；
- 监控：失败重试、超时、每日预算限制和审计日志；
- 部署：正式环境、支付、隐私与版权动作仍须单独审批。

**不要**在无人监管的容器内赋予 Docker Socket、无限网络权限、个人 GitHub 全权限凭据或不设上限的 API 调用预算。游戏商店付款/上架所需权限与研发执行器分开管理。

### 验收标准

- 私有仓库中可看到源代码与 `.github/workflows/` 目录；
- `OPC Quality Gate` 测试通过；
- `OPC Daily Brief` 能产生 GitHub Issue / artifact；
- 第一次手动 `OPC AI Daily Dev` 调用成功并产生 AI 工作摘要；
- AI 做出允许的改动且测试通过时，可以看到待审核 PR；
- `main` 未经你批准不会被 AI 改写；
- API Key 从未出现在日志、源码或 PR 中；
- 你能查看 GitHub Actions/API 实际用量与开支。

## 官方参考

- GitHub CLI: https://cli.github.com/manual/gh_repo_create
- OpenAI Codex Action: https://github.com/openai/codex-action
- Codex non-interactive mode: https://learn.chatgpt.com/docs/non-interactive-mode
- GitHub Actions permissions: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
