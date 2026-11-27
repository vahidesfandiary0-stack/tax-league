#!/usr/bin/env python3
import ast
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", "media", "staticfiles"}
results = []

def report(level, label, detail=""):
    results.append((level, label, detail))
    tags = {"PASS": "[موفق]", "WARN": "[هشدار]", "FAIL": "[خطا]", "SKIP": "[بررسی‌نشده]"}
    print("{} {}{}".format(tags[level], label, " — " + detail if detail else ""))

def git(*args):
    return subprocess.run(
        ["git"] + list(args), cwd=str(ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True
    )

print("=== RAQTIVA DEVELOPMENT AUDIT v1 ===")
print("حالت: فقط‌خواندنی | بدون اتصال به دیتابیس یا سرویس تولید")
print("مسیر:", ROOT)

r = git("rev-parse", "--show-toplevel")
if r.returncode == 0 and pathlib.Path(r.stdout.strip()).resolve() == ROOT:
    report("PASS", "ریشه مخزن Git")
else:
    report("FAIL", "ریشه مخزن Git", r.stderr.strip() or "مسیر با مخزن تطبیق ندارد")

r = git("rev-parse", "--short", "HEAD")
report("PASS" if r.returncode == 0 else "FAIL", "شناسه commit", r.stdout.strip() or r.stderr.strip())

r = git("branch", "--show-current")
branch = r.stdout.strip()
if r.returncode != 0:
    report("FAIL", "وضعیت شاخه", r.stderr.strip())
elif branch:
    report("PASS", "شاخه فعال", branch)
else:
    report("WARN", "حالت Git", "HEAD جداشده است؛ commit یا تغییر شاخه انجام ندهید")

r = git("status", "--porcelain")
if r.returncode == 0:
    changed = [line for line in r.stdout.splitlines() if line.strip()]
    report("WARN" if changed else "PASS", "وضعیت Working Tree",
           "{} مورد تغییر؛ هیچ‌کدام دست‌کاری نمی‌شود".format(len(changed)) if changed else "پاک")
else:
    report("FAIL", "وضعیت Working Tree", r.stderr.strip())

for args, label in [
    (("diff", "--check"), "کنترل patch تغییرات"),
    (("diff", "--cached", "--check"), "کنترل patch تغییرات staged"),
]:
    r = git(*args)
    report("PASS" if r.returncode == 0 else "FAIL", label,
           "بدون خطای whitespace" if r.returncode == 0 else r.stdout.strip() + r.stderr.strip())

python_files = []
for path in ROOT.rglob("*.py"):
    if any(part in SKIP for part in path.parts):
        continue
    if path.is_file():
        python_files.append(path)

syntax_errors = []
for path in python_files:
    try:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    except (SyntaxError, UnicodeError, OSError) as exc:
        syntax_errors.append("{}: {}".format(path.relative_to(ROOT), exc))

if syntax_errors:
    report("FAIL", "نحو Python", "{} خطا از {} فایل".format(len(syntax_errors), len(python_files)))
    for item in syntax_errors[:20]:
        print("   ", item)
else:
    report("PASS", "نحو Python", "{} فایل بدون خطای نحوی".format(len(python_files)))

tests = list((ROOT / "backend" / "tests").glob("test_*.py"))
report("PASS" if tests else "WARN", "فایل‌های آزمون Backend",
       "{} فایل آزمون شناسایی شد".format(len(tests)))

for tool in ("python3", "git", "docker", "flutter", "dart"):
    path = shutil.which(tool)
    report("PASS" if path else "SKIP", "ابزار " + tool, path or "در این محیط در PATH نیست")

print("\n=== خلاصه ===")
counts = {key: sum(1 for level, _, _ in results if level == key)
          for key in ("PASS", "WARN", "FAIL", "SKIP")}
print("موفق: {PASS} | هشدار: {WARN} | خطا: {FAIL} | بررسی‌نشده: {SKIP}".format(**counts))
print("این ممیزی جایگزین تست اجرایی، آزمون API، آزمون پرداخت یا بررسی دیتابیس نیست.")
sys.exit(1 if counts["FAIL"] else 0)
