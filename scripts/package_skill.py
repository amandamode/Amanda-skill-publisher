#!/usr/bin/env python3
"""把技能目录打包成可分发的 zip（可挂到 GitHub Release 上给别人下载）

用法:
  python3 package_skill.py <技能目录> [-o out.zip] [--dir-name 目录名] [--skip-validate]

规则:
  - zip 内第一层是技能目录，目录内含 SKILL.md（别人解压后要能直接放进技能目录）
  - 默认目录名取 SKILL.md 里的 name（技能标识），可用 --dir-name 覆盖
  - 排除 .git / __pycache__ / *.pyc / .DS_Store / *.zip / 真实 .env
  - 打包前自动跑 validate_skill.py，有 ERROR 直接中止
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
                ".idea", ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_EXT = {".pyc", ".zip", ".pyo", ".swp"}
KEEP_FILES = {"config.example.env"}


def read_skill_id(skill_dir):
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return None
    import re
    m = re.search(r"^name:\s*(\S+)", open(path, encoding="utf-8").read(), re.M)
    return m.group(1).strip("\"'") if m else None


def should_skip(rel, name):
    if name in EXCLUDE_FILES:
        return True
    if os.path.splitext(name)[1].lower() in EXCLUDE_EXT:
        return True
    if name.endswith(".env") and name not in KEEP_FILES:
        return True
    parts = rel.split(os.sep)
    return any(p in EXCLUDE_DIRS for p in parts)


def main():
    ap = argparse.ArgumentParser(description="把技能目录打包成可分发的 zip")
    ap.add_argument("skill_dir", help="技能目录（含 SKILL.md 的那一层）")
    ap.add_argument("-o", "--out", default=None, help="输出 zip 路径（默认 <技能目录>.zip）")
    ap.add_argument("--dir-name", default=None, help="zip 内首层目录名（默认取 SKILL.md 的 name）")
    ap.add_argument("--skip-validate", action="store_true", help="跳过打包前校验（不建议）")
    args = ap.parse_args()

    skill_dir = os.path.abspath(args.skill_dir)
    if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        sys.exit("✗ 技能目录里没有 SKILL.md")

    if not args.skip_validate:
        print("── 打包前校验 ──")
        r = subprocess.run([sys.executable, os.path.join(HERE, "validate_skill.py"), skill_dir])
        if r.returncode != 0:
            sys.exit("\n✗ 校验未通过，已中止打包。先修掉 ERROR。")

    dir_name = args.dir_name or read_skill_id(skill_dir) or os.path.basename(skill_dir)
    out = os.path.abspath(args.out) if args.out else os.path.abspath(skill_dir.rstrip("/") + ".zip")
    if os.path.exists(out):
        os.remove(out)

    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        stage = os.path.join(tmp, dir_name)
        os.makedirs(stage)
        for dirpath, dirnames, filenames in os.walk(skill_dir):
            rel_dir = os.path.relpath(dirpath, skill_dir)
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in filenames:
                rel = os.path.normpath(os.path.join(rel_dir, fn)) if rel_dir != "." else fn
                if should_skip(rel, fn):
                    continue
                src = os.path.join(skill_dir, rel)
                dst = os.path.join(stage, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                n += 1
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for dirpath, _dirs, files in os.walk(stage):
                for fn in files:
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, tmp))

    size_kb = os.path.getsize(out) / 1024
    print("\n── 打包完成 ──")
    print(f"  输出   : {out}")
    print(f"  体积   : {size_kb:.0f} KB ｜ 文件 {n} 个")
    print(f"  首层   : {dir_name}/  (含 SKILL.md)")
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        assert f"{dir_name}/SKILL.md" in names, "zip 内首层缺少 SKILL.md"
        assert not any(".git/" in x for x in names), "zip 内含 .git"
    print("  校验   : ✓ 首层含 SKILL.md   ✓ 无 .git")

    # 体积提示：挂到 Release 上给别人下载时，太大别人不愿下
    if os.path.getsize(out) > 5 * 1024 * 1024:
        print(f"\n  ! 体积 {size_kb/1024:.1f} MB 偏大，挂 Release 时别人可能不愿下载")
        print("    → 压缩大文件 / 剔除用不到的大资源（视频、模型、字体）")

    print(f"\n下一步：")
    print(f"  1) 把这个 zip 挂到 GitHub Release 上（别人下载解压就能装）")
    print(f"     gh release create <tag> {os.path.basename(out)} --title \"<tag>\" --notes-file RELEASE.md")
    print(f"  2) 或直接用 git 分享源码：目录名「{dir_name}」就是技能标识，别人 clone 后")
    print(f"     放进技能目录即可（见 references/skill-layout.md）")


if __name__ == "__main__":
    main()
