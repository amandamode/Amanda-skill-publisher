# 使用示例

## 场景一：一次完整发布（校验 → 打包 → 建仓推送 → 发 Release）

**用户视角**：

```
发布这个 skill：帮我校验、建仓、打 tag 并推到 GitHub
```

**skill 会依次做**：

1. `validate_skill.py` 校验 → 报 ERROR/WARN 清单，**有 ERROR 先修**
2. `package_skill.py` 打包 → 输出 zip 并打印内部结构（首层目录名 = 技能标识）
3. `publish_github.py` 建仓（若令牌有权限）+ 提交 + 打 tag + 推送
4. 提示下一步：发 Release（挂 zip）或直接用 git clone 分享
5. 交付：仓库地址、tag、zip 路径，以及"别人怎么装"的三句话说明

## 场景二：只检查能不能发布

```
这个技能包能给别人用吗？帮我查一下
```

只跑步骤 1，给出逐项结论与修复建议（不建仓、不推送）。

## 场景三：只打包，给别人下载

```
把这个技能目录打包成可分发的 zip，别人下载解压就能用
```

跑步骤 1–2，产出 zip。**关键点**：zip 首层目录名必须是技能标识，
别人解压后直接丢进技能目录就能被识别。

## 场景四：只推 GitHub

```
我要开源这个 skill，帮我建仓库、打 tag 并推上去
```

跑步骤 1（校验）+ 3（GitHub），跳过打包。

## 场景五：令牌过期了

```
我的 GitHub 令牌好像过期了，推不上去
```

跑 `github_device_flow.py` 换一把新的 → 写进钥匙串 → 重试推送。
注意 macOS 钥匙串要**先 erase 再 store**，否则 git 仍拿到旧的。

## 场景六：把仓库做成别人能直接用

```
帮我写清楚别人怎么获取和使用这个 skill
```

补 README 的「安装 / 配置 / 调用示例 / 目录结构」四个章节，
参考 `skill-layout.md` 里的模板。

## 手动调脚本

```bash
# 1) 校验
python3 scripts/validate_skill.py ../my-skill
python3 scripts/validate_skill.py ../my-skill --json      # CI 用
python3 scripts/validate_skill.py ../my-skill --strict    # WARN 也算不通过

# 2) 打包
python3 scripts/package_skill.py ../my-skill -o my-skill.zip
python3 scripts/package_skill.py ../my-skill --dir-name my-skill --skip-validate

# 3) 取令牌（首次 / 过期）
python3 scripts/github_device_flow.py --owner your-login --scopes "public_repo"

# 4) 发布
python3 scripts/publish_github.py ../my-skill \
    --repo-name my-skill --owner your-login \
    --visibility public --tag v1.0.0 \
    --message "feat: v1.0.0 — 初始发布" \
    --description "一句话描述这个技能"

# 5) 发 Release
gh release create v1.0.0 my-skill.zip --title "v1.0.0" --notes-file RELEASE.md
```

**退出码**：`validate_skill.py` 有 ERROR 时返回 1，可直接接进 CI 卡住提交。

## 一次真实跑通记录（2026-11-02）

| 环节 | 实测 |
|---|---|
| 校验对象 | 本技能包 v1.1.0，19 个文件 |
| 校验结果 | ERROR 0 / WARN 0（含结构、定义文件、引用完整性、绝对路径、密钥、脚本红线等 12 类检查） |
| 打包 | 47 KB，首层 `amanda-skill-publisher/SKILL.md`，无 `.git`、无真实密钥 |
| GitHub | 仓库 `amandamode/Amanda-skill-publisher`（Public），main + tag `v1.0.0` 推送成功，远端与本地 HEAD 一致 |
| 鉴权 | 设备码授权换 classic PAT（`public_repo`），存 macOS 钥匙串 |
| 踩坑 | ① App 令牌（`ghu_`）push 403 → 换用户级 PAT；② `osxkeychain store` 不覆盖旧条目 → 先 erase；③ 建仓必须走网页 UI（App 令牌无建仓权限）；④ 自己写校验器时，规则表里的违规样例会被自己的扫描器命中 → 模式改运行时拼接 |
