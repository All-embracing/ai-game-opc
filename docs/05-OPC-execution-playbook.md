# AI 游戏 OPC — 实施运行手册 V0.3

> 已实现：本地游戏原型、每日简报、GitHub Actions 开发候选流程、单元测试、代码补丁安全检查、离线部署自检。
> 未实现：任何真人玩家数据采集、正式游戏收入、实际 GitHub 仓库连接、在你的 GitHub 上成功运行、商店发行、真正持久化服务器。

## 1. 角色与权限表

| 角色 | 可执行 | 必须禁止 |
|---|---|---|
| 创始人 | 创建仓库、配置收费和密钥、批准 PR 与发行、授权 IP | 不向任何人共享密码或 API key |
| AI 策划 | 设计可验收小任务、候选文案、GDD | 自行承诺产品收益或版权 |
| AI 编程 | 仅修改 `games/ tests/ docs/`、运行受控测试、提候选补丁 | 修改 `.github/`、`scripts/`、密钥、支付、部署、账目 |
| 质量门禁 | 在无 OpenAI 密钥 job 中校验补丁、Python 测试和 JS 语法 | 失败时生成 PR、自动合并 |
| 运营助手 | 汇总已存在的真实测试、收入和成本 | 编造留存/投放回报/用户数量 |

## 2. 在 GitHub 上完成接入（需账号所有人操作）

1. 创建 GitHub **Private** 仓库 `ai-game-opc`，建议先使用专用组织或工作账号，开启 2FA。
2. 上传包含 `.github` 隐藏目录的完整工程；避免在本地忽略 `.github`。
3. 在 GitHub 项目 `Settings -> Secrets and variables -> Actions` 新增 Secret：`OPENAI_API_KEY`。只输入网页设置页面，不要发给 AI 或提交代码。
4. 在 OpenAI API 和 GitHub Billing 控制台配置预算提醒与账户级限制（以平台实际可配置项为准）；不要把 `studio.json` 内部预算当成真实平台硬限额。
5. 在 GitHub `Settings -> Actions -> General -> Workflow permissions` 允许 Actions 创建 Pull Request，但尽量保留默认 token 最小权限；权限按 workflow job 明确指定。
6. 先手动运行 `OPC Quality Gate`，再手动运行 `OPC Daily Brief`，检查产物以及 Issues 中的日报。
7. 最后手动运行 `OPC AI Daily Dev (Propose PR Only)`；它会调用 API 产生可能的费用。若三段 `propose -> verify -> submit_for_review` 成功并有有效改动，才会提交需要审批的 PR。
8. 先验收两次，确认权限、预算和 PR 质量，再配置 Actions Variable `ENABLE_AUTONOMOUS_CODING = true` 开启每日自动开发。
9. 对私有仓库启用支持该功能的仓库计划下的保护分支规则：强制 PR、测试成功、必要审核才能合并；不要启用自动合并。GitHub Free 对私有分支强制保护的可用性有限，应以当前官方套餐为准。

## 3. 每日任务循环

- 任务池：从 `data/backlog.json` 选择**一项** `agent_eligible=true` 且 `todo` 的工作。
- AI 写码：读取 `AGENTS.md` 和 `docs/AI_AGENT_TASK.md`；临时 Actions runner 修改本地工作树。
- 验证：把允许路径的补丁传给无 API 密钥的独立 job，先过 `scripts/policy_gate.py` 再执行测试。安全门禁仅做静态初筛，不能保证不存在恶意代码。
- 提交：只有测试成功，才由独立 job 创建待审核 PR；**不得自动合并、发布或付款**。
- 人工验收：负责人审查差异、实际玩一遍、确认美术/IP 使用权，决定合并或拒绝；合并后手动更新 backlog 状态。
- 复盘：更新真实实验记录、风险表、成本记录；日报不得把未知当 0。

## 4. 上线前补齐的能力

- 产品：先建立 15–50 人可重复玩法测试，追踪可验证的核心指标。
- 美术和音乐：以 `data/asset-register.csv` 记录素材来源与可商用许可；没有批准不能用于正式发行。
- 数据：明确事件协议、数据最小化、隐私披露、存储和同意机制；先使用本地匿名事件，不擅自外传玩家数据。
- 经营：单款游戏损益、渠道成本、退款及税务记录，成本来源可审计。
- 发行：Steam 商店资料、平台开发者账户、身份/收款/税务验证、内容与地区适用合规。
- 可靠性：版本号、备份恢复演练、报警通知、失败处理、审核台账、依赖与许可证核查。
- 支付与支持：涉及真实玩家付款或账号，另外引入安全后台及官方支付，不放在当前浏览器原型里。

## 5. 真正的“持久化 AI 环境”何时部署

**先用 GitHub 托管 runner 验证 2 周**，若每天任务运行时长、缓存、服务常驻等需求超过 GitHub Actions 的边界，再在合规地区部署独立云主机（Ubuntu + Docker + 队列 + Codex CLI + systemd + SSH/秘密管理）。它不是当前已部署组件；公网访问、安全维护、费用和权限属于需先获得你批准的操作。

云端执行器必须有：非 root 用户、短期或细粒度 GitHub 凭据、受限网络与容器资源、单任务超时与失败重试、审计日志、每日/每月成本告警、关键操作人工审批。部署建议使用独立隔离的工作负载，不直接把个人电脑当作无人监管的常驻执行器。

## 6. 接入验收（必须真实核对）

- [ ] GitHub 私有仓库可见 `.github/workflows`。
- [ ] GitHub Actions 质量测试绿色通过（提供运行链接）。
- [ ] GitHub Issue 的日报由实际 workflow 生成。
- [ ] OpenAI API Key 位于 GitHub Secrets，未出现在仓库或日志。
- [ ] Codex 真正执行了一次被计费或记录的任务，有具体运行链接。
- [ ] 非空改动通过安全门禁和测试，可看到 PR；失败时不会提 PR。
- [ ] 手动否决 PR 后 `main` 不会发生变更。
- [ ] 真实玩家数据、费用、利润尚未知时，报告明确写未知。
- [ ] 发版、版权、支付、税务和投入预算的最终责任由人承担。

## 7. 官方参考

- GitHub Actions 权限：https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- GitHub Actions 费用：https://docs.github.com/en/actions/concepts/billing-and-usage
- OpenAI Codex GitHub Action：https://github.com/openai/codex-action
- Codex 非交互模式：https://learn.chatgpt.com/docs/non-interactive-mode
