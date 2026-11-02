---
name: amanda-skill-publisher
display_name: Skill 发布助手（GitHub）
display_name_en: Skill Publisher for GitHub
description: 把本地技能目录校验、打包并发布到 GitHub 仓库（建仓、提交、打 tag、推送、生成 Release），并写清其他用户如何安装使用。当用户说「发布 skill」「把这个 skill 开源」「建仓并打 tag 推送」「打包成可分发的 zip」「让别人也能用这个 skill」时使用。
description_zh: 一条流水线把技能目录变成可开源的 GitHub 仓库：结构校验、打包、建仓提交打 tag 推送、生成 Release 与安装说明。
description_en: Turn a local skill directory into an open-source GitHub repository — validate, package, create the repo, commit, tag, push, and publish a Release with install instructions.
examples_zh:
- "发布这个 skill：帮我校验、建仓、打 tag 并推到 GitHub"
- "我要开源这个 skill，帮我建仓库、写 README 并让别人能装上"
- "把这个技能目录打包成可分发的 zip，别人下载解压就能用"
examples_en:
- "Publish this skill: validate, create the repo, tag and push to GitHub"
- "Open-source this skill with a proper README and install instructions"
- "Package this skill directory into a distributable zip"
version: 1.1.1
author: Amanda
allowed-tools: Bash, Read
---

# Skill 发布助手（发布到 GitHub）

把一个本地技能目录，变成一个**其他人都能用起来的开源 GitHub 仓库**：
结构校验 → 打包 → 建仓提交打 tag 推送 → 生成 Release 与安装说明。

## 元信息

| 项 | 值 |
|---|---|
| 技能标识 | `amanda-skill-publisher` |
| 版本 | 1.1.1 |
| 作者 | Amanda |
| 许可证 | MIT |
| 仓库 | https://github.com/amandamode/Amanda-skill-publisher |
| 运行环境 | macOS / Linux · Python 3.9+ 标准库 · git · GitHub 账号 |
| 依赖声明 | `requirements.txt`（**无第三方依赖**，无需 pip install） |
| 配置模板 | `config.example.env`（`GITHUB_TOKEN` / `GITHUB_OWNER` / `GITHUB_API_BASE`） |
| 仓库结构 | `@references/skill-layout.md` |
| 发布流程 | `@references/github-publish.md` |
| 排错 | `@references/faq.md` |

## 何时使用

- 用户要把一个技能**开源到 GitHub**（建仓、提交、打 tag、推送、发 Release）
- 用户要**打包**技能目录，给别人下载安装
- 用户要**检查一个技能包是否规范**（目录结构、定义文件、密钥泄露、脚本红线、可移植性）
- 用户要**写清别人如何获取和使用**这个技能（README 的安装与用法章节）

**不适用**：只是想改技能内容 → 直接改，别跑本技能；只想做本地目录整理 → `git init` 就够。

## 步骤

### 1. 先校验，再动手（别跳过）

```bash
python3 scripts/validate_skill.py <技能目录>
```

检查项：目录结构、**SKILL.md 定义文件**是否完备、frontmatter 字段规范、
references 目录里的文件引用是否都存在、本机绝对路径、真实密钥、脚本安全红线（下载后执行 / 读系统敏感目录）、打包卫生。

**有 ERROR 必须先修**——技能包是要给别人用的：结构乱、密钥泄漏、脚本有红线，别人装上就是坑。
判断依据见 `@references/skill-layout.md`。

### 2. 打包成可分发的 zip（可选，但推荐）

```bash
python3 scripts/package_skill.py <技能目录> -o <技能名>.zip
```

自动跑一遍校验 → 排除 `.git`/`__pycache__`/真实 `.env` → zip 首层放技能目录（目录名默认取 `SKILL.md` 里的 `name`）。

这个 zip 有两个用途：**挂到 GitHub Release 上**（别人直接下载解压就能装），或作为附件分发。

### 3. 发布到 GitHub

```bash
# 首次（或令牌过期）先取一个用户级 PAT，存进钥匙串
python3 scripts/github_device_flow.py --owner <你的ID> --scopes "public_repo"

# 建仓 + 提交 + 打 tag + 推送
python3 scripts/publish_github.py <技能目录> \
    --repo-name <技能名> --owner <你的ID> \
    --visibility public --tag v1.0.0 \
    --message "feat: v1.0.0 — <一句话说明>" \
    --description "<一句话描述这个技能>"
```

脚本自己解析鉴权（`--token-file` → 环境变量 `GITHUB_TOKEN` → macOS 钥匙串），
**不会把令牌写进 `.git/config` 或 remote URL**。没有令牌时它不瞎猜，
而是打印你可以直接复制执行的 git 命令。

**命名**：GitHub 仓库名建议统一加作者前缀（如 `Amanda-my-skill`）；
技能自己的标识（`SKILL.md` 的 `name`）保持小写连字符。

### 4. 写清「别人怎么用」——这一步决定仓库有没有人用

仓库的价值不在代码，在**别人能不能装上、能不能触发**。README 必须有：

| 章节 | 内容 |
|---|---|
| 功能特性 | 这个技能解决什么问题，一句话说清输入→输出 |
| 安装 | `git clone` + 软链到技能目录；或从 Release 下载 zip 解压 |
| 配置 | 需要哪些凭证/依赖，写明**填在哪里** |
| 调用示例 | 用户在对话里怎么说会触发它 |
| 目录结构 | 让人一眼看懂每个文件干什么 |

详细写法与目录规范见 `@references/skill-layout.md`。

### 5. 发一个 Release（可选但推荐）

打 tag 之后把 zip 挂上去，别人不用 clone 就能下载：

```bash
gh release create v1.0.0 <技能名>.zip --title "v1.0.0" --notes-file RELEASE.md
```

没有 `gh` 命令行时，也可以直接用 GitHub 网页端：Releases → Draft a new release → 选 tag → 拖 zip 进去。

`templates/release-notes.md` 是发布说明模板，填完即可。

### 6. 交付

回复中给出：校验结论（ERROR/WARN 数）、GitHub 仓库地址与 tag、zip 路径与体积、
Release 链接，以及**别人如何安装使用**的三句话说明。

## 前置依赖

| 依赖 | 说明 |
|---|---|
| Python 3 | 运行 `scripts/` 下四个脚本（**仅标准库**） |
| git | 建仓、提交、打 tag、推送 |
| GitHub 账号 | 令牌三选一：环境变量 `GITHUB_TOKEN` / `--token-file` / macOS 钥匙串 |
| 浏览器 | 仅在需要设备码授权时，人工在浏览器点一下授权即可 |

## 已知限制

- **令牌会过期**：classic PAT 有有效期，过期后只有"这台机器推不动"，仓库与代码不受影响；
  想要永久免密就换 SSH key（见 `@references/github-publish.md`）
- **App 类令牌（`ghu_`）不能写仓库**：它只有该 App 已安装的仓库能写，push 会 403
- **钥匙串不覆盖**：macOS `git credential-osxkeychain store` 不会覆盖同键旧条目，
  必须先 `erase` 再 `store`，否则 git 一直拿到旧令牌
- **技能标识 `name` 改了等于换一个新技能**：别人按旧名字装不上，要改就得重发一次

详细排错见 `@references/faq.md`；浏览器自动化的实战细节见 `@references/browser-automation.md`。
