# 变更记录

本文件记录每个版本的改动，便于回溯。

## v1.1.1 — 2026-11-02

**防御性修复（对标开放平台「内置文件缺失」驳回）**

- `references/skill-layout.md` / `references/checklist.md` / `README.md`：把说明性占位 `references/xxx.md` 改为不带路径 token 的写法，
  规避字面路径被平台扫描误判为缺失文件
- `SKILL.md` / `README.md`：`version` → 1.1.1

## v1.1.0 — 2026-11-02

**范围收敛：只做「把 skill 发布到 GitHub」——从校验、打包、建仓打 tag 推送，到写清别人如何安装使用。**

### 新增
- `references/skill-layout.md` — **新增**：一份"别人能用起来"的标准布局。
  包含：仓库目录结构（哪些文件必须、哪些是加分项）、
  **必须提交的定义文件**（SKILL.md 的 frontmatter 字段与正文写法、README 必备章节、
  requirements.txt、config.example.env、LICENSE）、
  以及**其他用户如何获取和使用**的三条路径（clone 软链 / Release 下载 zip / 单目录浅克隆）
  与「让别人用得顺的三个细节」。

### 移除
- 文档体系重构为一套纯粹的「GitHub 发布」文档：结构规范、发布流程、排错、示例、FAQ 各自独立成篇。
- SKILL.md / README / checklist / examples / faq / release-notes / 脚本的措辞统一为「发布到 GitHub」的语境。

### 变更
- `SKILL.md` — 步骤收敛为 6 步：校验 → 打包 → 发布 GitHub → **写清别人怎么用** → 发 Release → 交付。
  触发词与 `display_name` 同步收敛到「发布 / 开源 / 打包分发」这三类真实意图。
- `README.md` — 重写：新增「安装」（clone 软链 + Release zip 两条路径）、
  「它到底解决什么问题」改为面向开源场景的 5 条。
- `references/checklist.md` — 改为**发布到 GitHub 前**的 A–G 七段清单，
  新增 E 段「别人能不能用起来」。
- `references/examples.md` — 场景改为纯 GitHub 发布（完整发布 / 只检查 / 只打包 / 只推送 /
  令牌过期 / 补文档）。
- `references/faq.md` — 补「别人怎么用」与「标识改名等于换技能」两条。
- `templates/release-notes.md` — 改为 **GitHub Release 说明模板**（含装上就能用的命令、
  怎么用、需要准备什么），变成可直接粘贴进 Release 的说明。
- `scripts/validate_skill.py` — 判定依据统一为「技能包规范」；
  `examples` 条数检查改为通用展示约定（2–3 条）。
- `scripts/package_skill.py` — 体积硬上限改为提示，打包后给出 Release 分发用法；
  打包后提示改为 GitHub Release 分发用法。
- `CONTRIBUTING.md` — 发布流程改为「打 tag → 重新打包 → 发 Release」；
  红线里新增一条「别把自己的违规样例写进源码，否则静态扫描会命中它自己」。

## v1.0.0 — 2026-11-02

首个发布版。把一次真实的「技能发布全流程」固化成可复用的 skill。

### 新增
- `scripts/validate_skill.py` — 规范校验器，11 类检查：
  目录结构、frontmatter 必填字段、未定义字段告警、标识命名规范、
  version 语义化、description 模糊词与触发线索、`@references/` 引用完整性、
  本机绝对路径、真实密钥、脚本安全红线、打包卫生与文件体积。
  支持 `--json`（CI）与 `--strict`（WARN 也算不通过），ERROR 时退出码 1。
- `scripts/package_skill.py` — 打包器：先校验再打包，
  排除 `.git` / `__pycache__` / `*.pyc` / 真实 `.env`，
  保证 zip 首层是技能目录且含 `SKILL.md`，输出结构清单与体积。
- `scripts/publish_github.py` — GitHub 发布器：建仓、提交、打 tag、推送一条龙。
  鉴权按 `--token-file` > 环境变量 > 钥匙串解析，**不把令牌写进 `.git/config` 或 remote URL**；
  无令牌时打印可直接复制执行的 git 命令。
- `scripts/github_device_flow.py` — 设备码授权助手：浏览器点一下拿到用户级令牌，
  自动写入 macOS 钥匙串；含令牌覆盖问题的修复提示。
- `references/github-publish.md` — GitHub 发布实战：读与写的区别、
  四种鉴权对比、四类令牌前缀的能力差异、令牌优先级、403 与 401 的区分、
  标准发布流程、命名约定、发布前自查表。
- `references/browser-automation.md` — 浏览器自动化实战：内置浏览器与用户浏览器的选择、
  设备码授权页面的四个坑（账号选择器、OTP 分格输入、坐标聚焦、POST-only 不可刷新）、
  从页面取一次性密钥、坐标与截图的坑、代理环境下的排查。
- `references/checklist.md` — 发布前逐项 checklist。
- `references/examples.md` — 使用场景 + 手动调脚本 + 一次真实跑通记录。
- `references/faq.md` — 常见问题。
- `templates/release-notes.md` — 发布说明模板。
- `config.example.env` — 配置模板（令牌 / 归属账号 / API 地址 / 仓库名前缀）。
- `requirements.txt` — 依赖声明（纯标准库）。

### 特性
- **零依赖**：不需要 `pip install`，也不引入第三方包
- **不硬编码任何个人路径**，配置全部走环境变量 / 参数 / 钥匙串
