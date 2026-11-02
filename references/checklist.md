# 发布到 GitHub 前的 Checklist

打勾全过再推。**ERROR 项会坑到使用者**，WARN 项建议一起修掉。

## A. 目录与定义文件（机器可查）

- [ ] 技能根目录直接含 `SKILL.md`
- [ ] 子目录只用 `references/` `scripts/` `templates/`
- [ ] zip 内首层是技能目录，且 `首层/SKILL.md` 存在
- [ ] zip 内无 `.git`、无 `__pycache__`、无 `.DS_Store`、无嵌套 zip
- [ ] `@references/xxx.md` 里的每个文件都真实存在
- [ ] 单文件 < 2 MB，整体体积适中

**一条命令查完**：

```bash
python3 scripts/validate_skill.py <技能目录>
```

## B. SKILL.md 定义文件（人工确认）

- [ ] `name` 是合法标识：小写字母/数字/连字符，无空格，无中文
- [ ] `name` 与 README、zip 首层目录名**三处一致**
- [ ] `version` 是语义化版本，且与 README / CHANGELOG 一致
- [ ] `author` 是主体名称
- [ ] `description` 写的是**确定性触发场景**："什么输入 + 什么意图"，含具体触发词
- [ ] `description` **不含**模糊词：可能 / 也许 / 万能 / 支持所有 / 任意场景 / 百分百 / 包治
- [ ] `examples_zh` / `examples_en` 各 2–3 条，是**用户真实会说的话**
- [ ] frontmatter **没有**官方未定义的字段（homepage / repository / license / keywords…）
- [ ] 正文有「何时使用 / 不适用」，避免被误触发

## C. 安全与可移植性

- [ ] 全包 `grep -rn "/Users/" . --exclude-dir=.git` → **0 命中**
- [ ] 全包 `grep -rnE "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|wx[0-9a-f]{16}" . --exclude-dir=.git` → **0 命中**
- [ ] 真实凭证**不在包内**（只放使用者本地环境变量 / `.env`）
- [ ] 仓库里有 `config.example.env` 之类的**占位符模板**
- [ ] 脚本里没有「下载后直接交给 shell 执行」的管道形式
- [ ] 脚本里没有读取系统敏感目录的代码（用户信息文件 / SSH 私钥 / 系统钥匙串 / 进程环境变量）
- [ ] 脚本里没有提权执行
- [ ] 脚本在**干净环境**下可运行（`--help` 正常、`py_compile` 通过）
- [ ] 脚本不依赖本机绝对路径；配置一律走环境变量或参数

## D. 文档完整度

- [ ] README 有：功能特性 / 安装 / 配置 / 调用示例 / 目录结构 / 发布 / 许可证
- [ ] README 的目录结构树与实际文件一致
- [ ] README 顶部有元信息表（标识 / 版本 / 作者 / 许可证 / 仓库地址）
- [ ] README 的**安装**章节写了别人怎么装（clone 软链 + 下载 zip 两条路径）
- [ ] README 的**配置**章节写明每个配置项填在哪、优先级是什么
- [ ] README 的**调用示例**是用户会说的话（不是命令）
- [ ] 有 `CHANGELOG.md`
- [ ] 有 `LICENSE`（MIT 等）
- [ ] 有 `CONTRIBUTING.md`（含敏感信息红线）
- [ ] 有依赖声明 `requirements.txt`（**无依赖也要写明**）
- [ ] 有常见问题说明（FAQ 或 troubleshooting）

## E. 别人能不能用起来（最容易被忽略的一段）

- [ ] 从零 clone 到能跑通，**不超过 3 条命令**
- [ ] 有一个「五分钟能验证」的最小路径（一条可直接复制的命令）
- [ ] 解压 zip 后得到的目录名就是技能标识（放进技能目录就能被识别）
- [ ] 触发词与 README 的调用示例一致（不会出现"文档这么写但实际不触发"）
- [ ] 如果机器上可能装有触发词重叠的其它技能，README 里提了一句

## F. GitHub 侧

- [ ] 仓库名符合命名约定（建议加作者前缀，如 `Amanda-xxx`）
- [ ] 提交邮箱是 `<owner>@users.noreply.github.com`
- [ ] 仓库是 Public（开源用途）且 Description 已填
- [ ] 已打版本 tag，且指向正确提交（`git tag -l -n1`）
- [ ] README 里的仓库地址、命令与实际一致
- [ ] 已 push：`git ls-remote origin` 能看到 `refs/heads/main` 与 `refs/tags/vX.Y.Z`
- [ ] Release 已发，zip 附件可下载（别人不用 clone 也能拿到）

## G. 提交后

- [ ] 记录提交时间与 commit SHA
- [ ] 把仓库地址与安装方式写进你的项目文档 / 笔记
- [ ] 提醒自己：技能标识 `name` 改了等于换了一个新技能，旧名字的安装方式会失效
