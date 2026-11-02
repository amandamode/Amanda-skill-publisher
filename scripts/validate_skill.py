#!/usr/bin/env python3
"""WorkBuddy 开放平台 Skill 包校验器（仅标准库）

用法:
  python3 validate_skill.py <技能目录>            # 人类可读报告
  python3 validate_skill.py <技能目录> --json     # 机器可读（CI 用）
  python3 validate_skill.py <技能目录> --strict   # 有 WARN 也视为不通过

退出码: 0 = 通过(可能有 WARN)；1 = 存在 ERROR

校验项按官方《技能基础结构》《子资源目录说明》与实跑审核驳回点整理:
  1. 目录结构：SKILL.md 必须在技能根目录；子目录仅允许 references/ scripts/ templates/
  2. frontmatter：必填字段、字段值规范、slug 命名
  3. description：确定性触发场景，禁止模糊词
  4. 引用完整性：SKILL.md 里 @references/xxx.md 必须真实存在
  5. 禁止本机绝对路径（换机器就跑不起来）
  6. 禁止真实密钥入库
  7. 脚本安全：禁止下载后执行、禁止读取系统敏感目录
  8. 打包卫生：无 .git / __pycache__ / .DS_Store / 大文件
"""
import argparse
import json
import os
import re
import sys

# ── 官方 frontmatter 字段 ───────────────────────────────────────────
REQUIRED_FIELDS = ["name", "display_name", "description", "version", "author"]
OPTIONAL_FIELDS = ["display_name_en", "description_zh", "description_en",
                   "examples_zh", "examples_en", "allowed-tools"]
KNOWN_FIELDS = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)

ALLOWED_SUBDIRS = {"references", "scripts", "templates"}
# 允许出现在技能根目录的文件（平台不解析，但审核友好）
ALLOWED_ROOT_FILES = {
    "SKILL.md", "README.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md",
    "requirements.txt", "package.json", "config.example.env", ".gitignore",
    "NOTICE", "CODE_OF_CONDUCT.md", "SECURITY.md",
}

# description 里出现这些词会被判为「模糊」，审核易驳回
VAGUE_WORDS = ["可能", "也许", "万能", "什么都能", "支持所有", "任意场景", "百分百", "包治"]

# 真实密钥特征
SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub classic PAT"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"ghu_[A-Za-z0-9]{20,}", "GitHub user-to-server token"),
    (r"gh[osu]_[A-Za-z0-9]{30,}", "GitHub OAuth token"),
    (r"\bwx[0-9a-f]{16}\b", "微信 AppID（真实值）"),
    (r"(?i)WECHAT_SECRET\s*=\s*[0-9a-zA-Z]{16,}", "微信 AppSecret"),
    (r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][0-9a-zA-Z_\-]{20,}['\"]", "疑似硬编码密钥"),
    (r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----", "私钥文件内容"),
]

# 本机绝对路径
ABS_PATH_PATTERNS = [
    (r"/Users/[A-Za-z0-9._-]+/", "macOS 用户目录"),
    (r"/home/[A-Za-z0-9._-]+/", "Linux 用户目录"),
    (r"[A-Za-z]:\\\\?Users\\\\?", "Windows 用户目录"),
    (r"/Volumes/[A-Za-z0-9._-]+/", "macOS 外接卷"),
]

# 脚本安全红线
UNSAFE_SCRIPT_PATTERNS = [
    (r"curl[^|\n]*\|\s*(sudo\s+)?(ba)?sh", "下载后直接执行（curl | sh）"),
    (r"wget[^|\n]*\|\s*(sudo\s+)?(ba)?sh", "下载后直接执行（wget | sh）"),
    (r"eval\s*\(\s*(requests|urllib|urlopen|fetch)", "下载后 eval 执行"),
    (r"/etc/passwd", "读取系统敏感文件 /etc/passwd"),
    (r"\.ssh/id_[a-z0-9]+", "读取 SSH 私钥"),
    (r"Library/Keychains", "读取 macOS 钥匙串"),
    (r"security\s+find-(generic|internet)-password", "读取系统钥匙串凭证"),
    (r"/proc/[0-9]+/environ", "读取进程环境变量"),
    (r"sudo\b", "使用 sudo 提权"),
]

TEXT_EXT = {".md", ".py", ".js", ".ts", ".sh", ".json", ".yaml", ".yml", ".txt", ".html", ".env", ".example", ".cfg", ".ini", ".toml"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", ".pytest_cache", ".mypy_cache"}
MAX_FILE_MB = 2.0

# 规则表自身的行（形如  (r"正则", "说明") ）不算违规——
# 否则校验器会把自己规则表里的示例文字当成命中（自检型工具的经典假阳性）
RULE_TABLE_LINE = re.compile(r"^\s*[\(\[]\s*r?[\"']")


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, check, msg, fix=""):
        self.items.append({"level": level, "check": check, "msg": msg, "fix": fix})

    def error(self, c, m, f=""):
        self.add("ERROR", c, m, f)

    def warn(self, c, m, f=""):
        self.add("WARN", c, m, f)

    def ok(self, c, m):
        self.add("OK", c, m)

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "ERROR"]

    @property
    def warns(self):
        return [i for i in self.items if i["level"] == "WARN"]


def parse_frontmatter(text):
    """返回 (dict, body)。不是合法 frontmatter 时返回 (None, text)。"""
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return None, text
    raw, body = m.group(1), m.group(2)
    data = {}
    key = None
    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # 列表项（- "xxx"）归属上一个 key
        if re.match(r"^\s*-\s+", line):
            if key:
                data.setdefault(key + "_list", []).append(line.strip())
            continue
        km = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if km:
            key = km.group(1)
            val = km.group(2).strip()
            data[key] = val.strip("\"'") if val else ""
    return data, body


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            yield full, os.path.relpath(full, root)


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def validate(root):
    rep = Report()
    root = os.path.abspath(root)

    if not os.path.isdir(root):
        rep.error("结构", f"目录不存在：{root}")
        return rep

    skill_md = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill_md):
        rep.error("结构", "缺少 SKILL.md（必须在技能根目录）", "参照官方结构新建 SKILL.md")
        return rep
    rep.ok("结构", "SKILL.md 位于技能根目录")

    # ── 1. 目录结构 ──
    top = os.listdir(root)
    for name in top:
        p = os.path.join(root, name)
        if os.path.isdir(p):
            if name == ".git":
                continue          # git 仓库本身不算「非官方子目录」，打包时会被排除
            if name not in ALLOWED_SUBDIRS:
                rep.warn("结构", f"非官方子目录：{name}/",
                         "官方只解析 references/ scripts/ templates/；多余目录可能解析异常")
        elif name not in ALLOWED_ROOT_FILES:
            rep.warn("结构", f"根目录出现未登记文件：{name}",
                     "根级文件建议只用 README/LICENSE/CONTRIBUTING/CHANGELOG/requirements.txt 等")

    # ── 2. frontmatter ──
    text = read_text(skill_md) or ""
    fm, body = parse_frontmatter(text)
    if fm is None:
        rep.error("元信息", "SKILL.md 缺少 YAML frontmatter（--- 包裹）")
        fm = {}
    else:
        present = {k for k in fm if not k.endswith("_list")}
        for f in REQUIRED_FIELDS:
            if f in present and fm.get(f):
                rep.ok("元信息", f"必填字段 {f} 已填")
            else:
                rep.error("元信息", f"缺少必填字段 {f}")
        for f in sorted(present - KNOWN_FIELDS):
            rep.warn("元信息", f"出现官方未定义字段 {f}",
                     "官方仅支持 name/display_name(_en)/description(_zh/_en)/examples_zh/_en/"
                     "version/author/allowed-tools；多余字段可能被忽略甚至解析异常")
        for f in sorted(KNOWN_FIELDS - present):
            if f in OPTIONAL_FIELDS:
                rep.ok("元信息", f"可选字段 {f} 未填（不阻塞）")

        slug = fm.get("name", "")
        if slug:
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
                rep.error("元信息", f"name 不是合法 slug：{slug}",
                         "只允许小写字母、数字、连字符，且以字母或数字开头")
            else:
                rep.ok("元信息", f"name（slug）规范：{slug}")
        ver = fm.get("version", "")
        if ver and not re.fullmatch(r"\d+\.\d+\.\d+", ver):
            rep.warn("元信息", f"version 建议用语义化版本：{ver}", "形如 1.2.0")

    # ── 3. description 确定性 ──
    desc = fm.get("description", "") if fm else ""
    if desc:
        hit = [w for w in VAGUE_WORDS if w in desc]
        if hit:
            rep.error("元信息", f"description 含模糊词 {hit}",
                     "改成确定性场景 + 具体触发词（如「收到 v.douyin.com 链接并要求推到草稿箱时」）")
        else:
            rep.ok("元信息", "description 无模糊词")
        if len(desc) > 200:
            rep.warn("元信息", f"description 偏长（{len(desc)} 字）", "写清用途 + 触发词即可，别堆形容词")
        if not re.search(r"https?://|链接|「|用于|当用户|时", desc):
            rep.warn("元信息", "description 缺少触发线索",
                     "建议包含触发词与典型输入形态，便于被正确唤起")

    # ── 4. 引用完整性 ──
    refs = set(re.findall(r"@references/([A-Za-z0-9_.-]+\.md)", body))
    if not refs:
        rep.warn("引用", "SKILL.md 未引用任何 @references/*.md",
                 "细节应放进 references/ 并用 @ 引用，否则主文件会过长")
    for r in sorted(refs):
        if os.path.isfile(os.path.join(root, "references", r)):
            rep.ok("引用", f"@references/{r} 存在")
        else:
            rep.error("引用", f"@references/{r} 指向的文件不存在")

    # ── 5~7. 逐文件扫描 ──
    for full, rel in iter_files(root):
        ext = os.path.splitext(full)[1].lower()
        size_mb = os.path.getsize(full) / 1024 / 1024
        if size_mb > MAX_FILE_MB:
            rep.warn("打包卫生", f"{rel} 较大（{size_mb:.1f} MB）", "超过 2MB 的文件建议不进技能包")

        if rel.startswith(".git" + os.sep) or rel == ".git":
            rep.error("打包卫生", "包内含 .git 目录", "打包前排除 .git")
        if "__pycache__" in rel or rel.endswith(".pyc"):
            rep.error("打包卫生", f"含构建产物：{rel}")
        if rel.endswith(".DS_Store"):
            rep.warn("打包卫生", f"含系统文件：{rel}")
        if rel.endswith(".zip"):
            rep.warn("打包卫生", f"含 zip：{rel}", "发布包不要嵌套 zip")
        if rel.startswith("secrets/") or rel.endswith(".env") and not rel.endswith(".env.example"):
            if rel != "config.example.env":
                rep.error("密钥", f"疑似凭证文件入库：{rel}", "真实 .env 一律不进仓库")

        if ext not in TEXT_EXT and not rel.endswith("config.example.env"):
            continue
        content = read_text(full)
        if content is None:
            continue

        for pat, label in SECRET_PATTERNS:
            for m in re.finditer(pat, content):
                if "your-app-secret" in m.group(0) or "wx0000000000000000" in m.group(0):
                    continue
                rep.error("密钥", f"{rel} 含疑似{label}",
                          "真实密钥只放使用者本地（环境变量 / .env），不进包")
                break

        for pat, label in ABS_PATH_PATTERNS:
            for m in re.finditer(pat, content):
                # 文档里的示例路径允许，但脚本里的不允许
                is_script = rel.startswith("scripts" + os.sep)
                lvl = rep.error if is_script else rep.warn
                lvl("可移植性", f"{rel} 含{label}：{m.group(0)[:40]}",
                    "改用相对路径或环境变量" if is_script else "文档示例建议改成占位路径")
                break

        if rel.startswith("scripts" + os.sep):
            for pat, label in UNSAFE_SCRIPT_PATTERNS:
                hit = None
                for line in content.splitlines():
                    if RULE_TABLE_LINE.match(line):
                        continue          # 规则表自身的定义行不算违规
                    m = re.search(pat, line)
                    if m:
                        hit = line.strip()
                        break
                if hit:
                    rep.error("脚本安全", f"{rel} 命中红线：{label}（{hit[:60]}）",
                              "平台审核会驳回「下载后执行」「读取系统敏感目录」类脚本")
                    break
    return rep


def main():
    ap = argparse.ArgumentParser(description="校验 WorkBuddy 技能包是否符合开放平台规范")
    ap.add_argument("skill_dir", help="技能目录（含 SKILL.md 的那一层）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="WARN 也视为不通过")
    args = ap.parse_args()

    rep = validate(args.skill_dir)
    passed = not rep.errors and not (args.strict and rep.warns)

    if args.json:
        print(json.dumps({
            "skill_dir": os.path.abspath(args.skill_dir),
            "passed": passed,
            "errors": len(rep.errors),
            "warnings": len(rep.warns),
            "checks": rep.items,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 64)
        print(f"技能包校验：{os.path.abspath(args.skill_dir)}")
        print("=" * 64)
        for i in rep.items:
            icon = {"OK": "✓", "WARN": "!", "ERROR": "✗"}[i["level"]]
            print(f" {icon} [{i['check']}] {i['msg']}")
            if i["fix"] and i["level"] != "OK":
                print(f"     → {i['fix']}")
        print("-" * 64)
        print(f"  ERROR {len(rep.errors)} 项 ｜ WARN {len(rep.warns)} 项 ｜ "
              f"{'通过 ✓' if passed else '未通过 ✗'}")
        if not passed:
            print("  修复 ERROR 后再打包；平台审核会因结构/密钥/脚本红线直接驳回。")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
