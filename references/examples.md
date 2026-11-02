# 使用示例

## 场景一：一次发布（校验 → 打包 → 建仓推送 → 准备上架材料）

**用户视角**：

```
发布这个 skill：帮我校验、打包、建仓并推到 GitHub
```

**skill 会依次做**：

1. `validate_skill.py` 校验 → 报 ERROR/WARN 清单，**有 ERROR 先修**
2. `package_skill.py` 打包 → 输出 zip 并打印内部结构
3. `publish_github.py` 建仓（若 token 有权限）+ 提交 + 打 tag + 推送
4. 输出开放平台提交清单（表单项 + 审核演示说明 + 剩余待办）

## 场景二：只校验，不发布

```
这个技能包能过审吗？帮我查一下
```

只跑步骤 1，给出逐项结论与修复建议。

## 场景三：只打包上传开放平台

```
把这个技能目录打包成能传到开放平台的 zip
```

跑步骤 1–2，产出 zip + 平台表单填写建议。**上传与提交审核仍需用户自己点**。

## 场景四：只推 GitHub

```
帮我把这个 skill 开源，仓库名 Amanda-xxx，打 tag v1.0.0
```

跑步骤 1（校验）+ 3（GitHub）。

## 场景五：令牌过期了

```
我的 GitHub 令牌好像过期了，推不上去
```

跑 `github_device_flow.py` 换一把新的 → 写进钥匙串 → 重试推送。
注意 macOS 钥匙串要**先 erase 再 store**，否则 git 仍拿到旧的。

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
    --description "一句话描述这个 skill"
```

**退出码**：`validate_skill.py` 有 ERROR 时返回 1，可直接接进 CI 卡住提交。

## 一次真实跑通记录（2026-11-02）

| 环节 | 实测 |
|---|---|
| 校验对象 | `douyin-to-wechat-draft` v1.2.0，18 个文件 |
| 校验结果 | ERROR 0 / WARN 0（含 frontmatter、绝对路径、密钥、脚本红线、引用完整性 11 类检查） |
| 打包 | 42 KB，首层 `douyin-to-wechat-draft/SKILL.md`，无 `.git`、无真实密钥 |
| GitHub | 仓库 `amandamode/Amanda-douyin-to-wechat-draft`（Public），main + 三个 tag 全部推送成功 |
| 鉴权 | 设备码授权换 classic PAT（`public_repo`），存 macOS 钥匙串 |
| 踩坑 | ① App 令牌（`ghu_`）push 403 → 换用户级 PAT；② `osxkeychain store` 不覆盖旧条目 → 先 erase；③ 建仓必须走网页 UI（App 令牌无建仓权限） |
