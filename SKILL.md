---
name: skill-publisher
display_name: Skill 发布助手（GitHub + 开放平台）
display_name_en: Skill Publisher (GitHub + WorkBuddy Open Platform)
description: 把本地技能目录校验、打包并发布到 GitHub 仓库，同时产出 WorkBuddy 开放平台的提交材料。当用户说「发布 skill」「把这个 skill 开源」「打包传到开放平台」「上架技能」「skill 提交审核」「建仓并打 tag 推送」时使用。
description_zh: 一条流水线完成技能的合规校验、打包 zip、建仓推送 GitHub、生成开放平台提交清单与审核演示说明。
description_en: Validate, package, and publish a local skill to GitHub, plus prepare the WorkBuddy Open Platform submission package and review demo script.
examples_zh:
- "发布这个 skill：帮我校验、打包、建仓、打 tag 并推到 GitHub"
- "把这个技能目录打包成能传到开放平台的 zip"
- "帮我生成开放平台的提交材料和审核说明"
examples_en:
- "Publish this skill: validate, package, create the repo, tag and push to GitHub"
- "Package this skill directory into an uploadable zip for the open platform"
- "Generate the open-platform submission checklist and review demo script"
version: 1.0.0
author: Amanda
allowed-tools: Bash, Read
---

# Skill 发布助手（GitHub + WorkBuddy 开放平台）

把一个本地技能目录，变成「**可开源的 GitHub 仓库**」+「**可提交审核的开放平台 zip**」+「**一份能直接照着填的提交清单**」。

## 元信息

| 项 | 值 |
|---|---|
| 技能标识 | `skill-publisher`（平台 slug，全平台唯一，发布后不可改） |
| 版本 | 1.0.0 |
| 作者 | Amanda |
| 许可证 | MIT |
| 仓库 | https://github.com/amandamode/Amanda-skill-publisher |
| 适用平台 | WorkBuddy（macOS / Linux）· GitHub · WorkBuddy 开放平台 |
| 依赖 | **仅 Python 标准库**（无需 pip install） |
| 配置模板 | `config.example.env`（`GITHUB_TOKEN` / `GITHUB_OWNER` / `GITHUB_API_BASE`） |

## 何时使用

- 用户要把一个技能**开源到 GitHub**（建仓、提交、打 tag、推送）
- 用户要把技能**上传到 WorkBuddy 开放平台**（打包 zip、填元信息、过审核）
- 用户要**检查一个技能包是否合规**（结构、元信息、密钥泄露、脚本红线）
- 用户要**给审核准备材料**（提交清单、演示说明、变更记录）

**不适用**：
- 只是想改技能内容 → 直接改，别跑本 skill
- 非 WorkBuddy 的技能（如 npx skills 生态）→ 目标市场不同，流程不通用

## 步骤

### 1. 先校验，再动手（别跳过）

```bash
python3 scripts/validate_skill.py <技能目录>
```

按官方《技能基础结构》《子资源目录说明》+ 实测驳回点检查：目录结构、frontmatter 必填字段、
description 是否含模糊词、`@references/` 引用是否存在、本机绝对路径、真实密钥、
脚本红线（下载后执行 / 读系统敏感目录）、打包卫生。

**有 ERROR 必须先修**——平台审核会因这几项直接驳回。详细规则见 `@references/open-platform-spec.md`。

### 2. 打包成合规 zip

```bash
python3 scripts/package_skill.py <技能目录> -o <技能名>.zip
```

自动：跑一遍校验 → 排除 `.git`/`__pycache__`/`*.pyc`/真实 `.env` → zip 首层放技能目录（目录名默认取 `SKILL.md` 的 slug）。

**zip 结构硬要求**：首层是技能目录，且该目录内直接含 `SKILL.md`。

### 3. 发布到 GitHub

```bash
# 首次（或 token 过期）先取一个用户级 PAT，存进钥匙串
python3 scripts/github_device_flow.py --owner <你的ID> --scopes "public_repo"

# 建仓 + 提交 + 打 tag + 推送
python3 scripts/publish_github.py <技能目录> \
    --repo-name Amanda-<技能slug> --owner <你的ID> \
    --visibility public --tag v1.0.0 \
    --message "feat: v1.0.0 — <一句话说明>"
```

脚本会自己解析鉴权（环境变量 `GITHUB_TOKEN` → `--token-file` → macOS 钥匙串），
**不会把 token 写进 `.git/config` 或 remote URL**。没有 token 时它不会瞎猜，
而是打印你可以直接复制执行的命令。

**两套命名**：GitHub 仓库名建议统一加 `Amanda-` 前缀（作者约定）；
**平台 slug 不加前缀**，两者互不影响、不可混用。

### 4. 准备开放平台提交

打包完成后按 `@references/checklist.md` 准备：

1. **表单元信息**：技能名称（slug）、市场展示名称、能力介绍、市场展示分类、服务类目、图标、版本
2. **审核材料**：变更记录（`CHANGELOG.md`）+ 演示说明（`templates/release-notes.md`）
3. **上传**：open.workbuddy.cn → 添加技能 → 创建技能 → 上传 zip → 提交审核（1–3 个工作日）

`templates/release-notes.md` 是发布说明模板，填完即可作为审核佐证。

### 5. 交付

回复中给出：校验结论（ERROR/WARN 数）、GitHub 仓库地址与 tag、zip 路径与体积、
开放平台还差哪几项（通常只剩上传与提交审核）、以及**你必须手动点的那一步**。

## 前置依赖

| 依赖 | 说明 |
|---|---|
| Python 3 | **仅标准库**，无需 pip install |
| git | 建仓、提交、打 tag、推送 |
| 凭证 | GitHub token 三选一：环境变量 `GITHUB_TOKEN` / `--token-file` / macOS 钥匙串（`git credential-osxkeychain`） |
| 浏览器 | 仅在需要设备码授权时，人工在浏览器点一下授权即可 |

## 已知限制

- **上传与提交审核无法自动化**：平台表单含登录态与人工确认，最后一步必须用户自己点。
- **平台 slug 全局唯一且发布后不可改**：打包前务必先在平台上搜一遍确认未被占用。
- **GitHub 建仓需要 token 有建仓权限**：只有 `public_repo` scope 时 push 没问题，但
  `POST /user/repos` 可能被拒（`public_repo` 足以创建公开仓库，`repo` 更保险）。
- **App 类令牌（`ghu_`）不能用于写操作**：它只有该 App 已安装的仓库能写，push 会 403。
  详见 `@references/github-publish.md`。
- **钥匙串覆盖**：macOS `git credential-osxkeychain store` 不会覆盖已存在的同键条目，
  必须先 `erase` 再 `store`，否则 git 一直拿到旧令牌。

详细排错见 `@references/faq.md`；浏览器自动化的实战细节见 `@references/browser-automation.md`。
