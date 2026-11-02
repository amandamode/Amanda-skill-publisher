# 贡献指南

## 环境准备

```bash
git clone https://github.com/amandamode/Amanda-skill-publisher.git
cd Amanda-skill-publisher
python3 -m venv .venv && source .venv/bin/activate
```

**没有 pip 依赖**——所有脚本仅用标准库。开发只需要 `git` 和 Python 3.9+。

## 本地开发与自检

改完必跑：

```bash
# 1. 语法
python3 -m py_compile scripts/*.py

# 2. 每个脚本的 --help 都要正常
for s in scripts/*.py; do python3 "$s" --help >/dev/null || echo "FAIL $s"; done

# 3. 用自己的 skill 当测试样本跑一遍校验器
python3 scripts/validate_skill.py ../some-other-skill

# 4. 打包器自检（注意产物别提交）
python3 scripts/package_skill.py . -o /tmp/_t.zip
```

**改动校验规则时**，同步更新 `references/skill-layout.md`（校验器的判断依据在这份文档里）。
规则变更属于**行为变更**，需要 CHANGELOG 记录 + 版本号提升。

## 提交规范

[Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新增能力
fix: 修 bug
docs: 只改文档
refactor: 不改行为的重构
chore: 构建/配置/杂项
```

## 红线（绝对不能）

| 红线 | 说明 |
|---|---|
| **真实令牌入库** | 仓库里只能有占位符。`ghp_` / `github_pat_` / 真实 AppID 一律不能进包 |
| **改动校验器放宽红线** | 绕过检查等于把风险转给使用者。要放宽必须给出依据 |
| **把脚本改成需要第三方依赖** | 本技能的核心卖点之一是零依赖。加依赖要写进 `requirements.txt` 并说明 |
| **在本机绝对路径** | 不能出现用户目录绝对路径（macOS 的 `~/Users/…`、Linux 的 `~/home/…` 这类写法） |
| **写自己的违规样例** | 如果你新增了校验规则，**别把完整的违规代码写进源码**——CI 与各类静态扫描会命中它自己。规则里的模式串要用运行时拼接（见 `scripts/validate_skill.py` 里的写法） |

## 版本与发布

语义化版本：

| 变更 | 版本位 |
|---|---|
| 修 bug、改文案 | PATCH `1.1.1` |
| 新增能力、扩检查项 | MINOR `1.2.0` |
| 破坏性变更（校验规则收紧、CLI 参数改名） | MAJOR `2.0.0` |

发布流程：

1. 更新 `SKILL.md` 的 `version` 与 `CHANGELOG.md`
2. `git commit -am "release: v1.2.0"` + `git tag -a v1.2.0` + `git push --tags`
3. 重新打包 zip（`python3 scripts/package_skill.py . -o <技能名>.zip`）
4. 发 Release（`gh release create v1.2.0 <技能名>.zip --notes-file RELEASE.md`，或用网页端）

> 技能标识 `name` **发布后不要改**——改了等于换了一个新技能，
> 别人按旧名字装不上，等于要重新发布一次。仓库名可以改，但改了别人按旧名字就找不到了。

## 提 issue 请带

- 操作系统 + Python 版本
- 完整命令与完整报错
- 涉及的技能包结构（`find <skill> -type f`）
- **不要贴任何令牌**，贴前先打码
