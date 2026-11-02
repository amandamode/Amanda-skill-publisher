# skill 仓库的组织结构与定义文件

本文件回答三个问题：**一个能被别人用起来的 skill 仓库该长什么样**、
**必须提交哪些定义文件**、**别人拿到之后怎么装上并用起来**。

## 一、仓库目录结构（推荐布局）

```
{仓库名}/                        ← GitHub 仓库根目录
├── SKILL.md                      # ★ 技能定义文件（必须，见第二节）
├── README.md                     # ★ 给人看的门面（必须）
├── LICENSE                       # ★ 许可证（必须）
├── requirements.txt              # 依赖声明（无依赖也要写明）
├── config.example.env            # 配置模板（只有占位符，绝不放真凭证）
├── CHANGELOG.md                  # 变更记录
├── CONTRIBUTING.md               # 贡献指南（含敏感信息红线）
├── .gitignore                    # 忽略规则
├── references/                   # 细节资料（SKILL.md 用 @ 引用）
│   ├── <主题>.md
│   └── ...
├── scripts/                      # 可执行脚本
│   └── <脚本>.py
└── templates/                    # 模板文件
    └── <模板>.<ext>
```

**哪些是必须的、哪些是加分项**

| 文件 | 必须 | 不放会怎样 |
|---|---|---|
| `SKILL.md` | ✅ | 没有它这就不是一个技能，只是散装脚本，别人装不上也不会被触发 |
| `README.md` | ✅ | 别人打开仓库不知道这是什么、怎么装、怎么用 |
| `LICENSE` | ✅ | 别人不敢用（默认无授权 = 保留所有权利） |
| `requirements.txt` / `package.json` | ✅ | 别人不知道要装什么，装完直接报错 |
| `config.example.env` | 建议 | 别人不知道凭证填在哪，只能翻代码找 |
| `CHANGELOG.md` | 建议 | 升级时不知道改了什么 |
| `CONTRIBUTING.md` | 建议 | 别人想提 PR 不知道规矩 |
| `references/` `scripts/` `templates/` | 按需 | 细节全堆在 SKILL.md 里会变得没法读 |

> **目录名不要用空格、中文或大写**。zip 解压、路径引用、换系统都会出问题。
> 用小写连字符（`douyin-to-wechat-draft`）或仓库名原样。

## 二、必须提交的定义文件

### 1. `SKILL.md` —— 技能定义文件

两部分：**YAML frontmatter（机器读的元信息）** + **Markdown 正文（给 AI 看的执行说明）**。

#### frontmatter 字段

```yaml
---
name: my-skill                 # 技能标识：唯一、小写连字符，别人靠它安装
display_name: 我的技能          # 展示名
display_name_en: My Skill      # 英文展示名
description: 一句话说清用途和触发词。当用户说「xxx」「yyy」时使用。
description_zh: 简短中文介绍
description_en: Brief English intro
examples_zh:
- "用户会这么说：xxx"
- "用户会这么说：yyy"
examples_en:
- "How users will phrase it: xxx"
version: 1.0.0
author: 你的名字或组织
allowed-tools: Bash, Read      # 可选：工具白名单，逗号分隔
---
```

| 字段 | 要求 |
|---|---|
| `name` | 唯一标识。**改名等于换一个新技能**（旧名字的安装方式会失效），定名前先想清楚 |
| `description` | **最重要**。要写"什么输入 + 什么意图"，AI 靠它决定要不要触发。写"强大的多能工具"这种没用 |
| `examples_zh` / `examples_en` | 2–3 条最典型的用户原话。写多了会稀释触发词的权重 |
| `version` | 语义化版本 `主.次.修`。改了行为就提版本 |
| `allowed-tools` | 可选。限制 AI 能调用什么，缩小攻击面 |

> ⚠️ **别自造字段**。写 `homepage` / `repository` / `license` / `keywords` 这些
> 没有人读，还可能让读取它的工具行为异常。仓库地址、许可证这些写进正文和 README。

#### 正文写什么

正文是给 AI 看的执行说明，按"步骤"组织：

```markdown
# 一句话说明这个技能做什么

## 元信息        # 标识 / 版本 / 作者 / 仓库 / 运行环境 / 依赖声明
## 何时使用      # 什么情况下用、什么情况下不用
## 步骤          # 1. 2. 3.，每步给出可直接执行的命令
## 前置依赖      # 表格：依赖 | 说明
## 已知限制      # 会翻车的地方
```

**正文的黄金法则**：每一步都要给出**可直接复制的命令**，
并把细节（API 字段、错误码、格式约定）挪到 `references/` 里用 `@references/xxx.md` 引用。
`SKILL.md` 是入口，不是手册。

### 2. `README.md` —— 给人看的门面

README 决定"有没有人用"。必备章节：

```markdown
# 技能名（一句话说清做什么）

| 元信息 | 值 |          ← 标识 / 版本 / 作者 / 许可证 / 仓库地址 / 运行环境
|---|---|

## 功能特性      ← 3–6 条，每条一句话
## 安装          ← 两种方式：clone 软链 / 下载 zip
## 配置          ← 需要什么凭证，写明填在哪；配置项优先级
## 调用示例      ← 用户在对话里怎么说会触发
## 目录结构      ← 树状图，每个文件一句话说明
## 发布          ← 怎么打 tag、发 Release
## 许可证
```

### 3. `requirements.txt` —— 依赖声明

**没有第三方依赖也要写这个文件**，否则别人不知道你是真的不需要依赖：

```bash
# 无第三方依赖
# 本技能所有脚本仅使用 Python 标准库，无需 pip install。
#
# ── 系统依赖 ──────────────────────────────
# git       建仓 / 提交 / 打 tag / 推送
# Python 3.9+
```

有依赖时写清版本下限，并注明哪些是系统级（brew/apt 装，不走 pip）。

### 4. `config.example.env` —— 配置模板

**只放占位符**，并且在注释里写清楚每个配置项从哪拿、填在哪：

```bash
# 【必填】GitHub 用户级令牌
#   获取：Settings → Developer settings → Personal access tokens → Tokens (classic)
#   权限建议：public_repo（只推公开仓库）
GITHUB_TOKEN=ghp_your_token_here

# 【必填】仓库归属账号
GITHUB_OWNER=your-github-login

# 【可选】API 基地址，默认 https://api.github.com
GITHUB_API_BASE=https://api.github.com
```

**真实凭证永远不进仓库**。放在使用者本地（`~/.config/` 下的独立文件，或环境变量）。

### 5. `LICENSE` —— 别人敢不敢用

没有许可证，默认是"保留所有权利"，别人不敢用你的代码。
开源至少要有 MIT。版权人写清楚。

## 三、别人怎么获取和使用你的 skill

这是仓库能不能真正"活起来"的关键。**要在 README 里写清楚这三条路径。**

### 路径 A：从源码克隆（适合会折腾的人）

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>

# 装依赖（如果有）
pip install -r requirements.txt

# 让 WorkBuddy 能发现它：软链到技能目录
ln -s "$(pwd)/<repo>" ~/.workbuddy/skills/<skill-name>
```

装好后重启 / 刷新客户端，在对话里按 README 的「调用示例」那句话就能触发。

### 路径 B：从 Release 下载 zip（适合不想装环境的人）

在仓库 Releases 页下载 zip → 解压 → 把解压出来的技能目录放进技能目录：

```bash
unzip <repo>-v1.0.0.zip -d ~/.workbuddy/skills/
```

解压出来的目录名必须就是技能标识（打包器保证 zip 首层目录名 = `SKILL.md` 里的 `name`），
这样放进去才能被正确识别。

### 路径 C：直接 clone 单个目录（最轻）

```bash
git clone --depth 1 https://github.com/<owner>/<repo>.git ~/.workbuddy/skills/<skill-name>
```

### 触发方式

技能安装后，靠 `description` 里的触发词被唤醒。所以：

- `description` 写得越具体，命中越准
- `examples_zh` 里写的就是**用户真实会说的话**，照着那个语气写 README 的「调用示例」
- 同一台机器上装了触发词重叠的多个技能，会随机命中其中一个 —— 这是使用者的坑，
  README 里最好提一句

### 让别人用得顺的三个细节

1. **README 顶部要有元信息表**（标识 / 版本 / 许可证 / 仓库），别人第一眼就知道这是什么、能不能商用
2. **配置项要写清优先级**（命令行 > 环境变量 > 配置文件 > 默认值），否则别人改不动
3. **给一条"五分钟能跑通"的最小路径**：一个能直接复制粘贴验证的命令，
   让人不用读全文就知道这技能活着

## 四、发布前自检（速查）

```
□ SKILL.md 在仓库根目录，frontmatter 字段齐全
□ name 小写连字符、无空格、与 README 一致
□ description 写清"什么输入 + 什么意图"，含具体触发词
□ examples 2–3 条，是用户真实会说的话
□ README 有：功能特性 / 安装 / 配置 / 调用示例 / 目录结构 / 许可证
□ LICENSE 存在
□ requirements.txt 存在（无依赖也要写明）
□ 真实凭证不在仓库里，只有占位符模板
□ 脚本里没有本机绝对路径（换机器就跑不起来）
□ 脚本里没有下载后执行、没有读系统敏感目录
□ zip 首层是技能目录且含 SKILL.md
□ 已打版本 tag，且指向正确提交
□ README 写清了别人如何 clone / 下载 / 安装
```

更细的逐项清单见 `@references/checklist.md`。
