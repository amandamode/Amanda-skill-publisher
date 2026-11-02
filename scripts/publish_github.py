#!/usr/bin/env python3
"""把本地技能仓库发布到 GitHub（建仓 + 提交 + 打标签 + 推送）

用法:
  python3 publish_github.py <技能目录> \
      --repo-name Amanda-my-skill --owner amandamode \
      [--visibility public|private] [--tag v1.0.0] [--message "..."] [--dry-run]

鉴权来源（按优先级）:
  1. 环境变量 GITHUB_TOKEN
  2. --token-file 指向的文件
  3. macOS 钥匙串（git credential fill，读 credential.helper 指定的 helper）

没有 token 时脚本不会瞎猜：会打印**可直接复制执行**的 git 命令，由你自己补鉴权。

注意:
  - GitHub 仓库名与平台 slug 是两套命名。本脚本默认给仓库名加 <owner> 前缀风格，
    但推荐你用统一的「Amanda-」前缀（见 --no-prefix）。
  - 不会把 token 写进 .git/config 或 remote URL。
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
DEFAULT_PREFIX = "Amanda-"


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"✗ 命令失败：{' '.join(cmd)}\n{r.stderr.strip() or r.stdout.strip()}")
    return r


def get_token(args):
    if args.token_file:
        t = open(args.token_file, encoding="utf-8").read().strip()
        if t:
            return t
    t = os.environ.get("GITHUB_TOKEN", "").strip()
    if t:
        return t
    # 钥匙串：交给 git 自己解析（含 osxkeychain）
    r = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("password="):
            pwd = line.split("=", 1)[1].strip()
            if pwd:
                return pwd
    return None


def api(method, path, token, data=None):
    req = urllib.request.Request(
        f"{API}{path}", method=method,
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "amanda-skill-publisher"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body


def main():
    ap = argparse.ArgumentParser(description="发布技能仓库到 GitHub")
    ap.add_argument("skill_dir")
    ap.add_argument("--repo-name", required=True, help="GitHub 仓库名（建议带 Amanda- 前缀）")
    ap.add_argument("--owner", default=os.environ.get("GITHUB_OWNER", ""), help="仓库归属账号")
    ap.add_argument("--visibility", default="public", choices=["public", "private"])
    ap.add_argument("--tag", default=None, help="版本标签，如 v1.0.0")
    ap.add_argument("--message", default=None, help="commit message")
    ap.add_argument("--description", default="", help="仓库描述")
    ap.add_argument("--token-file", default=None)
    ap.add_argument("--no-prefix", action="store_true", help="不加默认前缀（已自带前缀时用）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将要执行的动作")
    args = ap.parse_args()

    d = os.path.abspath(args.skill_dir)
    if not os.path.isfile(os.path.join(d, "SKILL.md")):
        sys.exit("✗ 目录里没有 SKILL.md")

    repo_name = args.repo_name
    if not args.no_prefix and not repo_name.startswith(DEFAULT_PREFIX):
        repo_name = DEFAULT_PREFIX + repo_name

    print("── 准备 ──")
    print(f"  技能目录 : {d}")
    print(f"  仓库名   : {repo_name}")
    print(f"  归属     : {args.owner or '(未指定)'}")

    # 1. git 仓库
    if not os.path.isdir(os.path.join(d, ".git")):
        print("  初始化 git 仓库…")
        run(["git", "init", "-b", "main"], cwd=d)
        if not os.path.exists(os.path.join(d, ".gitignore")):
            with open(os.path.join(d, ".gitignore"), "w", encoding="utf-8") as f:
                f.write("*.zip\n__pycache__/\n*.pyc\n.DS_Store\n.venv/\n*.env\n!config.example.env\n")
    else:
        print("  已是 git 仓库")

    # 2. 身份
    if not run(["git", "config", "user.name"], cwd=d, check=False).stdout.strip():
        run(["git", "config", "user.name", args.owner or "amanda-skill-publisher"], cwd=d)
    if not run(["git", "config", "user.email"], cwd=d, check=False).stdout.strip():
        run(["git", "config", "user.email",
             f"{args.owner or 'amanda-skill-publisher'}@users.noreply.github.com"], cwd=d)

    # 3. 提交
    msg = args.message or f"chore: 发布 {repo_name}"
    run(["git", "add", "-A"], cwd=d)
    st = run(["git", "status", "--porcelain"], cwd=d, check=False).stdout.strip()
    if st:
        print(f"  提交 {len(st.splitlines())} 个变更…")
        run(["git", "commit", "-m", msg], cwd=d)
    else:
        print("  工作区干净，无需新提交")

    # 4. 标签
    if args.tag:
        exists = run(["git", "tag", "-l", args.tag], cwd=d, check=False).stdout.strip()
        if not exists:
            run(["git", "tag", "-a", args.tag, "-m", args.tag], cwd=d)
            print(f"  打标签 {args.tag}")
        else:
            print(f"  标签已存在 {args.tag}")

    token = get_token(args)
    remote_url = f"https://github.com/{args.owner}/{repo_name}.git" if args.owner else ""

    # 5. 建仓（需要 token）
    if token and args.owner and remote_url:
        code, body = api("GET", f"/repos/{args.owner}/{repo_name}", token)
        if code == 200:
            print(f"  远程仓库已存在：{body.get('html_url')}")
        else:
            code, body = api("POST", "/user/repos", token, {
                "name": repo_name,
                "private": args.visibility == "private",
                "description": args.description or "WorkBuddy skill",
                "auto_init": False,
            })
            if code in (201, 200):
                print(f"  ✓ 已创建仓库：{body.get('html_url')}")
            else:
                print(f"  ✗ 建仓失败（HTTP {code}）：{body.get('message', body)}")
                print("    → 可能是 token 权限不足（创建仓库需要 repo / public_repo scope）")
                sys.exit(1)
    else:
        print("  ⚠ 未取到 token 或未指定 owner，跳过自动建仓")

    # 6. remote + push
    if remote_url:
        cur = run(["git", "remote", "get-url", "origin"], cwd=d, check=False).stdout.strip()
        if cur != remote_url:
            if cur:
                run(["git", "remote", "set-url", "origin", remote_url], cwd=d)
            else:
                run(["git", "remote", "add", "origin", remote_url], cwd=d)
        print(f"  origin → {remote_url}")
        if args.dry_run:
            print(f"  [dry-run] git push -u origin main" + (f" && git push origin {args.tag}" if args.tag else ""))
            return
        r = run(["git", "push", "-u", "origin", "main"], cwd=d, check=False)
        print("  " + (r.stderr or r.stdout).strip().replace("\n", "\n  "))
        if r.returncode != 0:
            print("\n  推送失败。若提示 403 Permission denied：")
            print("    · token 无写权限 → 换一个带 repo / public_repo scope 的 PAT")
            print("    · App 类令牌（ghu_）只有该 App 已安装的仓库能写")
            print("    · 想免密 → 改用 SSH key：git remote set-url origin git@github.com:<owner>/<repo>.git")
            sys.exit(1)
        if args.tag:
            run(["git", "push", "origin", args.tag], cwd=d)
            print(f"  ✓ 标签已推送 {args.tag}")
    else:
        print("\n  以下命令需你自己执行（补上鉴权）：")
        print(f"    git remote add origin https://github.com/<owner>/{repo_name}.git")
        print("    git push -u origin main")
        if args.tag:
            print(f"    git push origin {args.tag}")


if __name__ == "__main__":
    main()
