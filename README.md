# Skill 发布助手（amanda-skill-publisher）

把一个本地技能目录，变成一个**其他人都能用起来的开源 GitHub 仓库**：
结构校验 → 打包 → 建仓提交打 tag 推送 → 生成 Release 与安装说明。

**纯标准库，零依赖**：`pip install` 都不用跑。

| 元信息 | 值 |
|---|---|
| 技能标识 | `amanda-skill-publisher` |
| 版本 | 1.1.0 |
| 作者 | Amanda |
| 许可证 | MIT |
| 仓库 | https://github.com/amandamode/Amanda-skill-publisher |
| 运行环境 | macOS / Linux · Python 3.9+ 标准库 · git · GitHub 账号 |
| 依赖 | **无第三方依赖**，见 `requirements.txt` |

## 功能特性

- **规范校验器**：12 类检查（目录结构、SKILL.md 定义文件、frontmatter 字段、标识命名规范、
  `examples` 条数、`@references/` 引用完整性、本机绝对路径、真实密钥、脚本安全红线、打包卫生、
  文件体积、依赖声明），输出逐项结论与修复建议，`--json` 可接 CI 卡提交
- **打包器**：自动排除 `.git`/`__pycache__`/真实 `.env`，保证 zip 首层是技能目录且含 `SKILL.md`
- **GitHub 发布器**：建仓 + 提交 + 打 tag + 推送一条龙；鉴权三选一（`--token-file` / 环境变量 / macOS 钥匙串），**不把令牌写进 `.git/config` 或 remote URL**
- **设备码授权助手**：在浏览器点一下就能拿到用户级令牌并写进钥匙串，**不需要把密码交给任何人**
- **仓库结构参考**：`references/skill-layout.md` 给出一份"别人能用起来"的标准布局，
  含 SKILL.md 定义文件写法、README 必备章节、以及别人 clone / 下载 / 安装的三条路径

## 安装

### 方式一：克隆源码（推荐）

```bash
git clone https://github.com/amandamode/Amanda-skill-publisher.git
cd Amanda-skill-publisher
# 无需 pip install —— 纯标准库
```

让它在 WorkBuddy 里可用（软链到技能目录）：

```bash
ln -s "$(pwd)/Amanda-skill-publisher" ~/.workbuddy/skills/amanda-skill-publisher
```

### 方式二：下载 Release 里的 zip

在仓库 [Releases](https://github.com/amandamode/Amanda-skill-publisher/releases) 下载 zip →
解压后把技能目录放进技能目录：

```bash
unzip amanda-skill-publisher-v1.1.0.zip -d ~/.workbuddy/skills/
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
| `GITHUB_OWNER` | `--owner` 参数 → 环境变量 → config 文件 | 命令行最高 |
| `GITHUB_API_BASE`（**API 地址**） | `--api-base` → 环境变量 → config 文件 → 默认 `https://api.github.com` | 命令行最高 |
| `GITHUB_REPO_PREFIX`（仓库名前缀） | config 文件，默认 `Amanda-` | — |

## 调用示例

**对话触发**（安装后在 WorkBuddy 里说）：

```
发布这个 skill：帮我校验、建仓、打 tag 并推到 GitHub
我要开源这个 skill，帮我建仓库、写 README 并让别人能装上
把这个技能目录打包成可分发的 zip，别人下载解压就能用
```

**手动调脚本**：

```bash
# 1) 校验（退出码 1 = 有 ERROR）
python3 scripts/validate_skill.py ../my-skill
python3 scripts/validate_skill.py ../my-skill --json      # CI
python3 scripts/validate_skill.py ../my-skill --strict    # WARN 也算不通过

# 2) 打包（可挂到 Release 上给别人下载）
python3 scripts/package_skill.py ../my-skill -o my-skill.zip

# 3) 取令牌（首次 / 过期）
python3 scripts/github_device_flow.py --owner your-login --scopes "public_repo"

# 4) 发布
python3 scripts/publish_github.py ../my-skill \
    --repo-name my-skill --owner your-login \
    --visibility public --tag v1.0.0 \
    --message "feat: v1.0.0 — 初始发布"

# 5) 发 Release（需要 gh 命令行，或用网页端）
gh release create v1.0.0 my-skill.zip --title "v1.0.0" --notes-file RELEASE.md
```

## 目录结构

```
amanda-skill-publisher/
├── SKILL.md                      # ★ 技能定义（frontmatter + 步骤 + 元信息）
├── README.md                     # 本文件
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # 贡献指南（本地开发 / 提交规范 / 敏感信息红线）
├── CHANGELOG.md                  # 变更记录
├── requirements.txt              # 依赖声明（仅标准库，无需安装）
├── config.example.env            # 配置模板（占位符，无密钥）
├── .gitignore
├── references/                   # 详细实现（SKILL.md 用 @references/ 引用各 .md）
│   ├── skill-layout.md           # skill 仓库的组织结构 + 定义文件写法 + 他人安装路径
│   ├── github-publish.md         # GitHub 发布 + 四种鉴权 + 403/401 排查
│   ├── browser-automation.md     # 浏览器自动化实战（设备码授权的坑）
│   ├── checklist.md              # 发布前逐项 checklist
│   ├── examples.md               # 使用示例 + 实跑记录
│   └── faq.md                    # 常见问题
├── scripts/                      # 可执行脚本（纯标准库）
│   ├── validate_skill.py         # 规范校验器
│   ├── package_skill.py          # 打包器
│   ├── publish_github.py         # GitHub 发布器
│   └── github_device_flow.py     # 设备码授权
└── templates/
    └── release-notes.md          # Release 发布说明模板
```

## 它到底解决什么问题

发布一个 skill，卡人的从来不是"写代码"，而是这几件琐事：

1. **不知道一个能给别人用的技能包该长什么样** → 校验器把 12 类要求变成逐项 pass/fail
2. **README 缺这缺那，别人装了不会用** → `references/skill-layout.md` 给出标准布局与必备章节
3. **`git push` 403 搞不清原因** → 鉴权文档分清了 401 与 403，以及四类令牌的差异
4. **打 tag、发 Release 全靠手工记忆** → 发布器一条龙，末尾打印可核对的仓库地址与 commit
5. **密钥差点进仓库** → 校验器扫真实密钥模式，`.gitignore` 默认忽略 `.env`

## 发布

### GitHub

仓库：https://github.com/amandamode/Amanda-skill-publisher
（命名遵循作者约定：开源 skill 仓库统一加 `Amanda-` 前缀；技能标识 `name` 保持小写连字符）

```bash
git init -b main
git remote add origin https://github.com/amandamode/Amanda-skill-publisher.git
git add -A
git commit -m "feat: v1.1.0 — 收敛为纯 GitHub 发布"
git tag -a v1.1.0 -m "v1.1.0"
git push -u origin main && git push origin v1.1.0
```

发 Release（网页端也可以：Releases → Draft a new release → 选 tag → 拖 zip 进去）：

```bash
gh release create v1.1.0 amanda-skill-publisher.zip --title "v1.1.0" --notes-file RELEASE.md
```

## 许可证

MIT —— 见 [LICENSE](./LICENSE)。贡献流程见 [CONTRIBUTING.md](./CONTRIBUTING.md)。
