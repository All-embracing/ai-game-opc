# 首次上传到已创建 GitHub 仓库（All-embracing 专用）

目标仓库：`https://github.com/All-embracing/ai-game-opc.git`

**仓库已经创建：不要再运行 `gh repo create`！**

## 1. Windows 准备

1. 安装 [Git](https://git-scm.com/downloads/win)、[Python 3](https://www.python.org/downloads/windows/) 和 [GitHub CLI](https://cli.github.com/)。
2. 解压本 ZIP，进入其中的 `opc-game-studio` 文件夹。请确认能看见 `README.md`、`.github`、`scripts`、`games` 文件夹。
3. 在此文件夹地址栏输入 `powershell` 并回车，打开 PowerShell。
4. 登录到 **All-embracing** 有写权限的 GitHub 账号：

   ```powershell
   gh auth login
   gh auth setup-git
   gh auth status
   ```

5. 首次使用 Git，还可能需要设置提交身份（邮箱用你自己的 GitHub 邮箱或 noreply 邮箱）：

   ```powershell
   git config --global user.name "All-embracing"
   git config --global user.email "YOUR_GITHUB_EMAIL"
   ```

6. 先在本地运行测试（可选但推荐）：

   ```powershell
   python -m unittest discover -s tests -v
   python scripts/doctor.py
   ```

7. 上传到**已经存在且没有任何提交的空仓库**：

   ```powershell
   python scripts/publish_existing_repo.py
   ```

   脚本会验证仓库地址、Git 身份、远程是否有提交。仅在远程仓库为空且你输入 `UPLOAD` 后，才会执行初始化和推送；不会强制推送或覆盖已有提交。

   如果远程已包含 README 或其他提交，脚本会停止。**这是正常的安全保护**，不要自行运行 `git push --force`。可先 `git clone https://github.com/All-embracing/ai-game-opc.git`，再将源码合并到克隆目录中正常提交；如果存在同名文件冲突，先检查比较。

## 2. GitHub 上验证

打开 `https://github.com/All-embracing/ai-game-opc`，应看到 `.github/workflows`、`games`、`tests`、`scripts` 等目录。

打开仓库的 `Actions` 页面。如果 GitHub 询问是否启用 Actions，请确认后手动运行 `OPC Quality Gate`。代码上传一般也会触发该检查。

仅当质量门禁通过以后，再决定是否手动运行 `OPC Daily Brief`。

## 3. 启用 AI 开发（会产生 API 费用，最后再做）

1. 先在 OpenAI API 项目内设置使用预算与告警；ChatGPT 订阅费不等于 API 额度。
2. 在仓库 `Settings → Secrets and variables → Actions → New repository secret` 设置 `OPENAI_API_KEY`。不要把密钥发给任何人，也不要发到聊天。
3. 在 `Settings → Actions → General` 检查 `Workflow permissions` 中的 `Allow GitHub Actions to create and approve pull requests`；如不可用需核对组织/账号权限。
4. `Actions → OPC AI Daily Dev (Propose PR Only) → Run workflow`。初次只手动运行，查看 `propose`、`verify`、`submit_for_review` 的执行记录和结果。没有代码差异时不会创建 PR。
5. 确认可靠且成本可控后，再在仓库 `Settings → Secrets and variables → Actions → Variables` 设置 `ENABLE_AUTONOMOUS_CODING=true`，允许每日定时启动（可能延迟）。
6. 审核后才能合并 PR。不要启用自动合并或自动正式发布。

## 4. 必须核查的事实

- 私有仓库由你掌控，未经本人授权，本项目无法代替你登录或直接 push。
- 此包包含本地已验收的基础工程和工作流配置；**不代表已经在你的 GitHub 账号成功运行**。
- 代码检查通过不等于游戏商业成功，IP、支付、上架仍需要人工审核。
- 如果下载文件不能预览，可直接在聊天中按照同样步骤操作。
