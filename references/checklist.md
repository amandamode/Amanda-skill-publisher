# 提交前 Checklist

打勾全过再上传。**ERROR 项必驳，WARN 项大概率驳。**

## A. 包结构（机器可查）

- [ ] 技能根目录直接含 `SKILL.md`
- [ ] 子目录只有 `references/` `scripts/` `templates/`
- [ ] zip 内首层是技能目录，且 `首层/SKILL.md` 存在
- [ ] zip 内无 `.git`、无 `__pycache__`、无 `.DS_Store`、无嵌套 zip
- [ ] `@references/xxx.md` 里的每个文件都真实存在
- [ ] 单文件 < 2 MB，整体体积适中

**一条命令查完**：

```bash
python3 scripts/validate_skill.py <技能目录>
```

## B. 元信息（人工确认）

- [ ] `name` 是合法 slug：小写字母/数字/连字符，无空格
- [ ] `name` **在平台上未被占用**（发布后不可改！）
- [ ] `version` 是语义化版本，且与 README / CHANGELOG 一致
- [ ] `author` 是主体名称
- [ ] `description` 写的是**确定性触发场景**，含具体触发词与输入形态
- [ ] `description` **不含**模糊词：可能 / 也许 / 万能 / 支持所有 / 任意场景 / 百分百 / 包治
- [ ] `examples_zh` / `examples_en` 各 2–3 条，能体现典型用法
- [ ] frontmatter **没有**官方未定义的字段（homepage / repository / license / keywords…）

## C. 安全与可移植性

- [ ] 全包 `grep -rn "/Users/" . --exclude-dir=.git` → **0 命中**
- [ ] 全包 `grep -rnE "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|wx[0-9a-f]{16}" . --exclude-dir=.git` → **0 命中**
- [ ] 真实凭证**不在包内**（只放使用者本地环境变量 / `.env`）
- [ ] 仓库里有 `config.example.env` 之类的**占位符模板**
- [ ] 脚本里没有「下载后直接交给 shell 执行」的管道形式（见 open-platform-spec.md 的红线表）
- [ ] 脚本里没有读取系统敏感目录的代码（用户信息文件 / SSH 私钥 / 系统钥匙串 / 进程环境变量）
- [ ] 脚本里没有提权执行（避免用管理员权限跑任何命令）
- [ ] 脚本在**干净环境**下可运行（`--help` 正常、`py_compile` 通过）
- [ ] 脚本不依赖本机绝对路径；配置一律走环境变量或参数

## D. 文档完整度

- [ ] README 有：功能特性 / 安装 / 配置 / 调用示例 / 目录结构 / 仓库地址
- [ ] README 的目录结构与实际文件一致
- [ ] 有 `CHANGELOG.md`（审核要看的"版本说明"）
- [ ] 有 `LICENSE`（MIT 等）
- [ ] 有 `CONTRIBUTING.md`（贡献指南，含敏感信息红线）
- [ ] 有依赖声明（`requirements.txt` 或 `package.json`）；纯标准库也要写明
- [ ] 有常见问题说明（FAQ 或 troubleshooting）
- [ ] 有使用示例
- [ ] 关键配置项（访问令牌 / API 地址等）**写明了填写位置**

## E. GitHub 侧

- [ ] 仓库名符合命名约定（GitHub 加 `Amanda-` 前缀，平台 slug 不加）
- [ ] 提交邮箱是 `<owner>@users.noreply.github.com`
- [ ] 已打版本 tag，且指向正确提交（`git tag -l -n1`）
- [ ] README 里的仓库地址、命令与实际一致
- [ ] 已 push：`git ls-remote origin` 能看到 `refs/heads/main` 与 `refs/tags/vX.Y.Z`

## F. 开放平台表单

| 字段 | 填什么 | ✓ |
|---|---|---|
| 技能名称 | 与 SKILL.md 的 `name` 一致 | [ ] |
| 市场展示名称 | 中文短名 | [ ] |
| 头像 | 512×512、≤500KB、JPG/PNG | [ ] |
| 市场展示分类 | 如「内容创作」（可多选） | [ ] |
| 服务类目 | 如「工具」（必填，1–5 个） | [ ] |
| 能力介绍 | 一句话说清输入→输出 | [ ] |
| 版本 | 与 SKILL.md 的 `version` 一致 | [ ] |
| 技能包 | 上传 zip | [ ] |

## G. 审核材料

- [ ] 演示说明（`templates/release-notes.md` 填好）：完整跑一遍的步骤 + 实测数据
- [ ] 变更记录（`CHANGELOG.md`）
- [ ] 一份"使用前后对比"或真实跑通证据（标题、字数、图片数、草稿 ID 之类）

## H. 提交后

- [ ] 提交审核，记录提交时间
- [ ] 审核 1–3 个工作日；被驳回时对照上面的 A–D 段定位
- [ ] 通过后：安装一次、在真实场景触发一次、确认触发词命中
- [ ] 同步更新 GitHub README 的版本号与变更记录
