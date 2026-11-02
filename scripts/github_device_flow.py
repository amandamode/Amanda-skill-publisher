#!/usr/bin/env python3
"""GitHub 设备码授权（Device Flow）—— 在浏览器里点一下就能拿到 PAT

用法:
  python3 github_device_flow.py --owner amandamode [--scopes "public_repo repo"] [--no-store]

流程:
  1. 向 GitHub 申请设备码，打印一次性验证码与验证网址
  2. 你在浏览器里输入验证码并授权（无需输入密码，GitHub 已登录即可）
  3. 脚本轮询换取 access_token，并写入 macOS 钥匙串供 git 直接使用

为什么用它:
  - 终端 git push 需要「用户级 token」（PAT）；App 类令牌（ghu_）只有 App 已安装的仓库能写，
    push 会 403
  - 设备码流程不需要你把密码或令牌交给任何人，也不用离开当前会话
  - 拿到的 token 存进钥匙串后，git push 直接免密

注意:
  - 令牌权限越窄越好：只推公开仓库用 public_repo 足够
  - 验证码 15 分钟有效，只需输一次
  - 不想存进钥匙串就加 --no-store
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# GitHub CLI 的公开 OAuth client id（GitHub 第一方应用，无需注册自有应用）
DEFAULT_CLIENT_ID = "Iv1.b507a08c87ecfe98"
TOKEN_URL = "https://github.com/login/oauth/access_token"
DEVICE_URL = "https://github.com/login/device/code"


def post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser(description="GitHub 设备码授权，取用户级 PAT")
    ap.add_argument("--client-id", default=DEFAULT_CLIENT_ID)
    ap.add_argument("--scopes", default="public_repo",
                    help="逗号分隔的权限范围。公开仓库推送用 public_repo 即可；"
                         "需要建仓/私有仓库时加 repo")
    ap.add_argument("--owner", default="", help="GitHub 用户名（存钥匙串时用）")
    ap.add_argument("--no-store", action="store_true", help="不写入钥匙串，只打印")
    args = ap.parse_args()

    print("── 第 1 步：申请设备码 ──")
    info = post(DEVICE_URL, {"client_id": args.client_id, "scope": args.scopes})
    if "device_code" not in info:
        sys.exit(f"✗ 申请失败：{info}")
    print(f"  一次性验证码：{info['user_code']}")
    print(f"  打开这个网址：{info.get('verification_uri', 'https://github.com/login/device')}")
    print(f"  （若跳转到了账号选择页，用网址追加 ?skip_account_picker=true 可直接跳过）")
    print(f"  有效期 {info.get('expires_in', 900)} 秒 ｜ 请求的权限：{args.scopes}")
    print("\n  → 在浏览器里输入验证码并点授权，然后回来等它自动完成（可 Ctrl-C 中止）")

    print("\n── 第 2 步：等待授权 ──")
    token = None
    deadline = time.time() + int(info.get("expires_in", 900))
    interval = int(info.get("interval", 5))
    waited = 0
    while time.time() < deadline:
        time.sleep(interval)
        waited += interval
        r = post(TOKEN_URL, {
            "client_id": args.client_id,
            "device_code": info["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        if "access_token" in r:
            token = r["access_token"]
            print(f"  ✓ 授权成功（等待 {waited}s）")
            break
        err = r.get("error")
        if err == "authorization_pending":
            print(f"  … 等待中（{waited}s）")
        elif err == "slow_down":
            interval += 5
            print(f"  … 降速重试（{waited}s）")
        elif err == "expired_token":
            sys.exit("✗ 验证码已过期，重新运行本脚本")
        elif err == "access_denied":
            sys.exit("✗ 你拒绝了授权")
        else:
            print(f"  ? {r}")
    if not token:
        sys.exit("✗ 超时，未取到令牌")

    print(f"  令牌长度 {len(token)} ｜ 前缀 {token[:4]}…")

    if args.no_store:
        print(f"\n  令牌（仅本次有效，请自行保存）：\n  {token}")
        return

    print("\n── 第 3 步：写入 macOS 钥匙串 ──")
    owner = args.owner
    if not owner:
        try:
            req = urllib.request.Request("https://api.github.com/user", headers={
                "Authorization": f"Bearer {token}", "User-Agent": "skill-publisher"})
            with urllib.request.urlopen(req, timeout=20) as r:
                owner = json.loads(r.read().decode()).get("login", "")
        except Exception:
            owner = ""
    if not owner:
        print("  ⚠ 未能自动识别用户名，请手动执行：")
        print(f'     printf "protocol=https\\nhost=github.com\\nusername=<你的ID>\\npassword={token}\\n\\n" '
              "| git credential-osxkeychain store")
        return

    p = subprocess.run(["git", "credential-osxkeychain", "store"],
                       input=f"protocol=https\nhost=github.com\nusername={owner}\npassword={token}\n\n",
                       capture_output=True, text=True)
    if p.returncode != 0:
        print(f"  ⚠ 写钥匙串失败：{p.stderr.strip()}")
        print(f"     手动执行：printf 'protocol=https\\nhost=github.com\\nusername={owner}\\npassword={token}\\n\\n' "
              "| git credential-osxkeychain store")
        return
    print(f"  ✓ 已写入钥匙串（username={owner}）")
    print("\n  现在可以直接 git push 了。若仍 403，先清掉旧条目再写：")
    print(f'     printf "protocol=https\\nhost=github.com\\nusername={owner}\\n\\n" | git credential-osxkeychain erase')


if __name__ == "__main__":
    main()
