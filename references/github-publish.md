# GitHub 发布实战（含鉴权与今日踩坑全记录）

本文件回答一个问题：**为什么 `git push` 会 403，以及到底该怎么授权。**

## 一、先理解：GitHub 上"读"和"写"是两件事

`clone` / `pull` 公开仓库可以匿名；`push` 是**改动他人服务器上的共享状态**，
服务器必须先确认"你是谁、你有没有权改这个仓库"。这就是鉴权的由来。

浏览器里上传文件之所以不用配置任何东西，是因为**登录 cookie 已经替你证明过身份**了。
命令行是一条独立的通道，必须自带凭证。

## 二、四种鉴权方式

| 方式 | 凭证形态 | 存在哪 | 每次推送 | 适用 | 怎么撤销 |
|---|---|---|---|---|---|
| **HTTPS + PAT** | 一串 token | 钥匙串 / 每次手输 | 每次带 token | 一次性、CI、脚本 | Settings → Developer settings → 撤销 |
| **SSH Key** | 密钥对 | 私钥 `~/.ssh/id_ed25519`、公钥在 GitHub | **免密**（签名证明身份） | 长期高频本地开发 | 删掉 GitHub 上的公钥 |
| **gh CLI** | 内部还是 token | `~/.config/gh/hosts.yml` | 免密（自动注入） | 命令行一体化（建仓/发 Release/开 PR） | `gh auth logout` |
| **网页端上传** | 浏览器 cookie | 浏览器 | 不需要 | 一次性、少量文件 | 退出登录 |

一句话对比：**PAT 是每次出示通行证，SSH 是门口认指纹不用每次查，gh CLI 是通行证 + 自动刷卡机。**

## 三、令牌前缀一眼看权限（今日血泪）

| 前缀 | 类型 | 能否 push |
|---|---|---|
| `ghp_` | classic PAT（用户级） | ✅ 取决于 scope |
| `github_pat_` | fine-grained PAT（用户级） | ✅ 取决于权限 |
| `ghu_` | **GitHub App 的 user-to-server token** | ❌ **只能写该 App 已安装的仓库** |
| `ghs_` | App 的 server-to-server token | ❌ 服务端专用 |

> **实战教训**：用设备码授权拿到的 `ghu_` 令牌，`GET /user` 正常、`POST /user/repos` 报
> `Resource not accessible by integration`、`git push` 报
> `Permission to <owner>/<repo>.git denied to <owner>`。
> 原因：App 令牌只对**已安装该 App 的仓库**有效，新建仓库不在其中。
> **解法**：改用用户级 PAT（classic，`public_repo` scope 即可推公开仓库）。

## 四、令牌优先级（最容易翻车的地方）

```
1. 命令行 --api-base / --token-file 参数
2. 环境变量 GITHUB_TOKEN
3. --env / config 文件
4. macOS 钥匙串（git credential helper 读出来的）
```

**macOS 钥匙串的坑**：`git credential-osxkeychain store` **不会覆盖已存在的同键条目**。
你存了新令牌但 git 还是拿到旧的，表现就是「明明换了 token 还是 403」。
修法：

```bash
printf "protocol=https\nhost=github.com\nusername=<你的ID>\n\n" | git credential-osxkeychain erase
printf "protocol=https\nhost=github.com\nusername=<你的ID>\npassword=<新token>\n\n" | git credential-osxkeychain store
# 验证：printf "protocol=https\nhost=github.com\n\n" | git credential fill
```

验证输出里的 `password=` 前缀，是判断「拿到的是哪把钥匙」最快的办法。

## 五、拿到用户级 PAT 的三种方式

### 方式 A：设备码授权（推荐，脚本已封装）

```bash
python3 scripts/github_device_flow.py --owner <你的ID> --scopes "public_repo"
```

它做的事：申请一次性验证码 → 你在浏览器输入并授权 → 换取 token → 写进钥匙串。
**你不需要把密码或令牌交给任何人**。

### 方式 B：网页手动创建 PAT

GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate。
**勾 `public_repo`** 即可（只推公开仓库）。注意 AppSecret 类值只显示一次。

### 方式 C：SSH key（一次性配置，永久免密）

```bash
ssh-keygen -t ed25519 -C "your@email" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
# 复制输出 → GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com   # 验证
```

之后把 remote 换成 SSH 地址即可：

```bash
git remote set-url origin git@github.com:<owner>/<repo>.git
```

## 六、标准发布流程

```bash
# 1. 初始化
git init -b main
git remote add origin https://github.com/<owner>/<repo>.git

# 2. 身份（没配过就要配）
git config user.name  "<owner>"
git config user.email "<owner>@users.noreply.github.com"

# 3. 提交与标签
git add -A
git commit -m "feat: v1.0.0 — <一句话>"
git tag -a v1.0.0 -m "v1.0.0"

# 4. 推送
git push -u origin main
git push origin v1.0.0
```

> **私有邮箱**：`<owner>@users.noreply.github.com` 是 GitHub 提供的私密邮箱，
> 不会暴露真实邮箱到公开仓库的提交记录里。

## 七、仓库命名约定

| 目标 | 规则 | 例 |
|---|---|---|
| **GitHub 仓库名** | 统一加作者前缀 | `Amanda-douyin-to-wechat-draft` |
| **平台 slug** | 不加前缀、小写连字符 | `douyin-to-wechat-draft` |

两套命名互不影响，但**在文档里要写清区别**，否则使用者会以为该用哪个。

## 八、发布前自查

- [ ] `.gitignore` 覆盖 `*.zip` / `__pycache__` / `*.env`（且放行 `config.example.env`）
- [ ] 提交邮箱是 `users.noreply.github.com`
- [ ] 没有绝对路径（`grep -rn "/Users/" . --exclude-dir=.git`）
- [ ] 没有真实密钥（`grep -rnE "ghp_[A-Za-z0-9]{20,}|wx[0-9a-f]{16}" . --exclude-dir=.git`）
- [ ] README 里有仓库地址、安装、配置、调用示例、目录结构
- [ ] tag 指向正确的提交（`git tag -l -n1`）
