# Skill 发布助手（amanda-skill-publisher）

把一个本地技能目录，变成「**可开源的 GitHub 仓库**」+「**可提交审核的开放平台 zip**」+「**一份能直接照着填的提交清单**」。

**纯标准库，零依赖**：`pip install` 都不用跑。

| 元信息 | 值 |
|---|---|
| 技能标识（平台 slug） | `amanda-skill-publisher`（全平台唯一，发布后不可改） |
| 版本 | 1.0.0 |
| 作者 | Amanda |
| 许可证 | MIT |
| 仓库 | https://github.com/amandamode/Amanda-skill-publisher |
| 适用平台 | WorkBuddy（macOS / Linux）· GitHub · WorkBuddy 开放平台 |
| 依赖 | Python 3.9+ 标准库 + git |

## 功能特性

- **合规校验器**：11 类检查（目录结构、frontmatter、slug 规范、description 模糊词、`@references` 引用完整性、本机绝对路径、真实密钥、脚本红线、打包卫生、字段值规范、依赖声明），输出逐项结论与修复建议，`--json` 可接 CI 卡提交
- **合规打包器**：自动排除 `.git`/`__pycache__`/真实 `.env`，保证 zip 首层是技能目录且含 `SKILL.md`
- **GitHub 发布器**：建仓 + 提交 + 打 tag + 推送一条龙；鉴权三选一（环境变量 / `--token-file` / macOS 钥匙串），**不把 token 写进 `.git/config` 或 remote URL**
- **设备码授权助手**：在浏览器点一下就能拿到用户级 PAT 并写进钥匙串，**不需要把密码交给任何人**
- **提交材料生成**：开放平台表单项建议 + 审核演示说明模板 + 逐段 checklist

## 安装

```bash
git clone https://github.com/amandamode/Amanda-skill-publisher.git
cd Amanda-skill-publisher
# 无需 pip install —— 纯标准库
```

**在 WorkBuddy 里用**：从 [开放平台](https://open.workbuddy.cn) 技能市场搜索 `amanda-skill-publisher` 安装，
或把本目录软链到 skills 目录：

```bash
ln -s "$(pwd)/Amanda-skill-publisher" ~/.workbuddy/skills/amanda-skill-publisher
```

## 配置

GitHub 凭证三选一，按优先级：

| 优先级 | 来源 | 说明 |
|---|---|---|
| 1 | `--token-file <文件>` | 脚本参数，最明确 |
| 2 | 环境变量 `GITHUB_TOKEN` | CI 场景推荐 |
| 3 | macOS 钥匙串 | `git credential-osxkeychain` 读出来的 |

配置模板见 `config.example.env`（**只有占位符**）：

```bash
mkdir -p ~/.workbuddy/secrets
cp config.example.env ~/.workbuddy/secrets/github-publish.env
$EDITOR ~/.workbuddy/secrets/github-publish.env
```

```ini
GITHUB_TOKEN=ghp_your_token_here     # 可选：也可不填，走设备码授权自动写钥匙串
GITHUB_OWNER=your-github-login       # 必填：仓库归属账号
GITHUB_API_BASE=https://api.github.com  # 可选：API 地址，一般不改
```

**关键配置项填写位置**

| 配置项 | 填写位置 | 优先级 |
|---|---|---|
| `GITHUB_TOKEN` | `--token-file` → 环境变量 → 钥匙串 | 命令行最高 |
| `GITHUB_OWNER` | 环境变量 / `--owner` 参数 → config 文件 | 命令行最高 |
| `GITHUB_API_BASE`（**API 地址**） | `--api-base` → 环境变量 → config 文件 → 默认 `https://api.github.com` | 命令行最高 |
| `GITHUB_REPO_PREFIX`（仓库名前缀） | config 文件，默认 `Amanda-` | — |

## 调用示例

**对话触发**（安装后在 WorkBuddy 里说）：

```
发布这个 skill：帮我校验、打包、建仓并推到 GitHub
把这个技能目录打包成能传到开放平台的 zip
我要开源这个 skill，帮我建仓库、打 tag、推上去
帮我生成开放平台的提交材料和审核说明
```

**手动调脚本**：

```bash
# 1) 校验（退出码 1 = 有 ERROR）
python3 scripts/validate_skill.py ../my-skill
python3 scripts/validate_skill.py ../my-skill --json      # CI
python3 scripts/validate_skill.py ../my-skill --strict    # WARN 也算不通过

# 2) 打包
python3 scripts/package_skill.py ../my-skill -o my-skill.zip

# 3) 取令牌（首次 / 过期）
python3 scripts/github_device_flow.py --owner your-login --scopes "public_repo"

# 4) 发布
python3 scripts/publish_github.py ../my-skill \
    --repo-name my-skill --owner your-login \
    --visibility public --tag v1.0.0 \
    --message "feat: v1.0.0 — 初始发布"
```

## 目录结构

```
amanda-skill-publisher/
├── SKILL.md                      # ★ 技能定义（frontmatter + 步骤 + 元信息）
├── README.md                     # 本文件
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # 贡献指南
├── CHANGELOG.md                  # 变更记录
├── requirements.txt              # 依赖声明（仅标准库，无需安装）
├── config.example.env            # 配置模板（占位符，无密钥）
├── .gitignore
├── references/                   # 详细实现（SKILL.md 用 @references/xxx.md 引用）
│   ├── open-platform-spec.md     # 开放平台规范 + 驳回点 + 表单字段
│   ├── github-publish.md         # GitHub 发布 + 四种鉴权 + 403/401 排查
│   ├── browser-automation.md     # 浏览器自动化实战（设备码授权的坑）
│   ├── checklist.md              # 提交前逐项 checklist
│   ├── examples.md               # 使用示例 + 实跑记录
│   └── faq.md                    # 常见问题
├── scripts/                      # 可执行脚本（纯标准库）
│   ├── validate_skill.py         # 合规校验器
│   ├── package_skill.py          # 合规打包器
│   ├── publish_github.py         # GitHub 发布器
│   └── github_device_flow.py     # 设备码授权
└── templates/
    └── release-notes.md          # 发布说明 / 审核演示说明模板
```

## 它到底解决什么问题

发布一个 skill，卡人的从来不是"写代码"，而是这几件琐事：

1. **不知道平台要什么格式** → 校验器把 11 类要求变成逐项 pass/fail
2. **zip 打包总被驳回**（首层不对、含 `.git`、含密钥）→ 打包器保证结构
3. **`git push` 403 搞不清原因** → 鉴权文档分清了 401 与 403，以及四类令牌的差异
4. **开放平台表单不知道填什么** → 表单字段逐项建议 + 演示说明模板
5. **要写一堆重复文档** → README / CONTRIBUTING / CHANGELOG / FAQ 的现成骨架

## 发布

### WorkBuddy 开放平台

```bash
python3 scripts/package_skill.py . -o amanda-skill-publisher.zip
```

1. zip 首层为 `amanda-skill-publisher/` 且含 `SKILL.md` ✅（打包器已保证）
2. open.workbuddy.cn → 添加技能 → 创建技能 → 上传 zip
3. 表单填写建议见 `references/checklist.md` F 段
4. 提交审核（1–3 个工作日）

### GitHub

仓库：https://github.com/amandamode/Amanda-skill-publisher
（命名遵循作者约定：开源 skill 仓库统一加 `Amanda-` 前缀；平台 slug 不加前缀）

```bash
git init -b main
git remote add origin https://github.com/amandamode/Amanda-skill-publisher.git
git add -A
git commit -m "feat: v1.0.0 — Skill 发布助手"
git tag -a v1.0.0 -m "v1.0.0"
git push -u origin main && git push origin v1.0.0
```

## 许可证

MIT —— 见 [LICENSE](./LICENSE)。贡献流程见 [CONTRIBUTING.md](./CONTRIBUTING.md)。
