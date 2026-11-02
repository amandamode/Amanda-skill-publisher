# 常见问题（FAQ）

## 校验

**Q：`validate_skill.py` 报「出现官方未定义字段」，可我看了官方文档确实有 homepage？**
A：官方技能规范的 frontmatter 只定义了 11 个字段：
`name` `display_name` `display_name_en` `description` `description_zh` `description_en`
`examples_zh` `examples_en` `version` `author` `allowed-tools`。
没有 homepage / repository / license / keywords / tags / platforms。
想表达这些，放 SKILL.md 正文元信息块 + README 表格。

**Q：报错里有 `/Users/xxx/`，但那只是文档里的示例路径，也要改吗？**
A：脚本里出现就是 ERROR（换机器跑不起来）；文档里出现是 WARN（建议改成占位路径）。

**Q：`wx0000000000000000` 被判成真实 AppID？**
A：占位符是 16 个 0，扫描器已排除。真实 AppID 是 `wx` + 16 位十六进制且不全为 0。

**Q：能校验别人的 skill 吗？**
A：能，校验器只看目录结构与内容，不联网、不执行被校验的脚本。

## 打包

**Q：zip 的第一层到底放什么？**
A：放**技能目录**，且该目录内直接含 `SKILL.md`，即
`my-skill.zip` → `my-skill/` → `SKILL.md`。
（注意：不是把 SKILL.md 直接放在 zip 根目录。）

**Q：目录名和平台 slug 不一致行不行？**
A：行，但建议一致，减少困惑。`package_skill.py` 默认用 SKILL.md 里的 `name` 作为首层目录名，
可用 `--dir-name` 覆盖。

**Q：能排除掉某些文件吗？**
A：脚本固定排除 `.git` / `__pycache__` / `*.pyc` / `*.zip` / 真实 `.env`（保留 `config.example.env`）。
其他自定义排除项建议在源目录用 `.gitignore` 控制后再打包。

## GitHub 发布

**Q：push 报 `Permission to xxx.git denied to xxx`？**
A：按顺序查三件事：
1. token 类型对不对——`ghu_`（App 令牌）**不能写**，必须是 `ghp_` / `github_pat_` 用户级令牌
2. scope 对不对——推公开仓库要 `public_repo`，推私有仓库要 `repo`
3. 钥匙串是不是还在给旧的——`printf "protocol=https\nhost=github.com\n\n" | git credential fill` 看前缀，
   不对就**先 erase 再 store**

**Q：建仓报 `Resource not accessible by integration`？**
A：用的是 App 类令牌。换成用户级 PAT（classic，`repo` 或 `public_repo`）再建仓；
或在网页上先建好空仓库，本地 `git remote add origin` 后直接推。

**Q：403 和 401 分别是什么意思？**
A：**401** = 令牌无效/过期/没带上（去换令牌）；**403** = 令牌有效但**权限不够**
（scope 不足，或令牌类型根本不适用于该操作）。两者别混。

**Q：token 会过期吗？**
A：会。classic PAT 有有效期（我给这次建的设了 30 天）。过期后只有"这台机器推不动"，
仓库和代码不受影响。想要永久免密就换 SSH key。

**Q：怎么确认包里没有本机绝对路径？**
A：跑校验器（它会逐文件扫），或手动搜用户目录写法。
命中在脚本里是 ERROR（换机器跑不起来），在文档里是 WARN（建议改成占位写法）。

**Q：要不要设 `credential.helper`？**
A：要。`git config --global credential.helper osxkeychain`（macOS），
这样令牌存钥匙串而不是每次手输。

**Q：两套命名怎么区分？**
A：**GitHub 仓库名**加作者前缀（`Amanda-xxx`），**平台 slug** 不加前缀（`xxx`）。
两套互不影响，但文档里要写清。

## 开放平台

**Q：能替我把 zip 传上去吗？**
A：不能。平台表单需要你的登录态与人工提交，且审核是人工流程。
本 skill 负责把包校验到能过审、把表单项和演示说明准备好，**最后那一下上传+提交必须你点**。

**Q：slug 被占用了怎么办？**
A：换一个新 slug，**三处同步改**：SKILL.md 的 `name`、zip 内首层目录名、README 里提到的 slug。
改完重新打包。

**Q：审核要准备什么材料？**
A：`CHANGELOG.md`（版本说明）+ 一份演示说明（`templates/release-notes.md` 填好：
完整流程步骤 + 一次真实跑通的实测数据）。见 `checklist.md` 的 G 段。

**Q：审核要多久？**
A：通常 1–3 个工作日。

## 浏览器自动化

**Q：设备码授权页面的按钮点不动？**
A：见 `browser-automation.md`——账号选择页要用 `?skip_account_picker=true` 跳过；
验证码输入框必须**逐字用真实按键事件**输入，且第一个框要用**坐标点击**聚焦；
确认页是 POST-only，**不能刷新**。

**Q：复制图标点了，剪贴板里没有 token？**
A：DOM 点击不写系统剪贴板，要用**坐标点击**那个图标。

**Q：页面一直 ERR_TIMED_OUT？**
A：先 `curl` 测同一域名。代理进程活着但上游节点挂了的时候，浏览器怎么点都没用。
