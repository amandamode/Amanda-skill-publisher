# 变更记录

## v1.0.0 — 2026-11-02

首个发布版。把一次真实的「技能发布全流程」固化成可复用的 skill。

### 新增
- `scripts/validate_skill.py` — 合规校验器，11 类检查：
  目录结构、frontmatter 必填字段、官方未定义字段告警、slug 命名规范、
  version 语义化、description 模糊词与触发线索、`@references/` 引用完整性、
  本机绝对路径、真实密钥、脚本安全红线、打包卫生与文件体积。
  支持 `--json`（CI）与 `--strict`（WARN 也算不通过），ERROR 时退出码 1。
- `scripts/package_skill.py` — 合规打包器：先校验再打包，
  排除 `.git` / `__pycache__` / `*.pyc` / 真实 `.env`，
  保证 zip 首层是技能目录且含 `SKILL.md`，输出结构清单与体积。
- `scripts/publish_github.py` — GitHub 发布器：建仓、提交、打 tag、推送一条龙。
  鉴权按 `--token-file` > 环境变量 > 钥匙串解析，**不把令牌写进 `.git/config` 或 remote URL**；
  无令牌时打印可直接复制执行的 git 命令。
- `scripts/github_device_flow.py` — 设备码授权助手：浏览器点一下拿到用户级 PAT，
  自动写入 macOS 钥匙串；含令牌覆盖问题的修复提示。
- `references/open-platform-spec.md` — 开放平台规范实测版：结构要求、
  frontmatter 11 个字段、脚本红线、发布表单字段、驳回原因、发布后能改什么。
- `references/github-publish.md` — GitHub 发布实战：读与写的区别、
  四种鉴权对比、四类令牌前缀的能力差异、令牌优先级、403 与 401 的区分、
  标准发布流程、命名约定、发布前自查表。
- `references/browser-automation.md` — 浏览器自动化实战：内置浏览器与用户浏览器的选择、
  设备码授权页面的四个坑（账号选择器、OTP 分格输入、坐标聚焦、POST-only 不可刷新）、
  从页面取一次性密钥、坐标与截图的坑、代理环境下的排查。
- `references/checklist.md` — 提交前逐项 checklist（包结构 / 元信息 / 安全可移植 / 文档 / GitHub / 表单 / 审核材料 / 提交后）。
- `references/examples.md` — 五个使用场景 + 手动调脚本 + 一次真实跑通记录。
- `references/faq.md` — 常见问题（校验 / 打包 / GitHub / 开放平台 / 浏览器自动化）。
- `templates/release-notes.md` — 发布说明与审核演示说明模板。
- `config.example.env` — 配置模板（令牌 / 归属账号 / API 地址 / 仓库名前缀）。
- `requirements.txt` — 依赖声明（纯标准库）。

### 特性
- **零依赖**：不需要 `pip install`，也不引入第三方包
- **不硬编码任何个人路径**，配置全部走环境变量 / 参数 / 钥匙串
- **只做能做的**：打包与推送全自动；平台上传与提交审核必须用户自己点
