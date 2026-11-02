# 常见问题（FAQ）

## 校验

**Q：校验器报「出现未定义字段」，可我看了文档确实有 homepage？**
A：技能定义文件（frontmatter）里只放机器会读的字段。
仓库地址、许可证、作者主页这类信息写在**正文元信息块 + README** 里，
不要往 frontmatter 塞——没人读，还可能让读取它的工具行为异常。

**Q：报错里提到用户目录绝对路径，但只是文档里的示例，也要改吗？**
A：脚本里出现就是 ERROR（换机器跑不起来），文档里出现是 WARN（建议改成占位写法）。

**Q：`wx0000000000000000` 被判成真实 AppID？**
A：占位符是 16 个 0，扫描器已排除。真实 AppID 是 `wx` + 16 位十六进制且不全为 0。

**Q：能校验别人的 skill 吗？**
A：能，校验器只看目录结构与内容，不联网、不执行被校验的脚本。

## 打包

**Q：zip 的第一层到底放什么？**
A：放**技能目录**，且该目录内直接含 `SKILL.md`，即
`my-skill.zip` → `my-skill/` → `SKILL.md`。
（不是把 SKILL.md 直接放在 zip 根目录。）

**Q：目录名和技能标识不一致行不行？**
A：行，但**建议一致**——别人解压后要把它放进技能目录才能被识别，
目录名 = 技能标识时最省事。打包器默认就跟随 `SKILL.md` 里的 `name`。

**Q：能排除掉某些文件吗？**
A：脚本固定排除 `.git` / `__pycache__` / `*.pyc` / `*.zip` / 真实 `.env`（保留 `config.example.env`）。
其他自定义排除项建议在源目录用 `.gitignore` 控制后再打包。

**Q：zip 有什么大小限制吗？**
A：没有硬性限制，但**挂到 Release 上给人下载**时建议控制在几 MB 内
（太大别人不愿意下）。打包器会对超过 5 MB 的包给出提示。

## GitHub 发布

**Q：push 报 `Permission to xxx.git denied to xxx`？**
A：按顺序查三件事：
1. 令牌类型对不对——`ghu_`（App 令牌）**不能写**，必须是 `ghp_` / `github_pat_` 用户级令牌
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
A：会。classic PAT 有有效期。过期后只有"这台机器推不动"，
仓库和代码不受影响。想要永久免密就换 SSH key。

**Q：要不要设 `credential.helper`？**
A：要。`git config --global credential.helper osxkeychain`（macOS），
这样令牌存钥匙串而不是每次手输。

**Q：仓库名和技能标识怎么区分？**
A：**GitHub 仓库名**建议加作者前缀（`Amanda-xxx`）；**技能标识**（`SKILL.md` 的 `name`）
保持小写连字符。两者相互独立，但 README 里要写清区别。

**Q：技能标识改了会怎样？**
A：**等于换了一个新技能**——别人按旧名字装不上，等于要重新发布一次。
所以定名前想清楚，发布后别改。

## 别人怎么用

**Q：别人装了之后怎么触发？**
A：靠 `description` 里的触发词被唤醒。所以 `description` 要写清"什么输入 + 什么意图"，
`examples_zh` 里写的就是用户真实会说的话。

**Q：同一台机器装了触发词重叠的多个技能会怎样？**
A：会随机命中其中一个，行为不确定。这是使用者的坑，
README 里最好提一句，或者让两个技能的触发词互斥。

**Q：不想让别人 clone 怎么办？**
A：发一个 Release，把打包好的 zip 作为附件挂上去，别人下载解压就能装。
`templates/release-notes.md` 是发布说明模板。

## 浏览器自动化

**Q：设备码授权页面的按钮点不动？**
A：见 `browser-automation.md`——账号选择页要用 `?skip_account_picker=true` 跳过；
验证码输入框必须**逐字用真实按键事件**输入，且第一个框要用**坐标点击**聚焦；
确认页是 POST-only，**不能刷新**。

**Q：复制图标点了，剪贴板里没有令牌？**
A：DOM 点击不写系统剪贴板，要用**坐标点击**那个图标。

**Q：页面一直 ERR_TIMED_OUT？**
A：先 `curl` 测同一域名。代理进程活着但上游节点挂了的时候，浏览器怎么点都没用。
