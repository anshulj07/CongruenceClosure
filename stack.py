import random
import subprocess
from datetime import datetime

# --- CONFIG ---
file_path = "core/closure.py"
possible_comments = [
    "# TODO: optimize this later",
    "# NOTE: check logic here",
    "# DEBUG: investigate edge case",
    "# HACK: temporary fix 😬",
    "# REVIEW: revisit this section"
]

commit_messages = [
    "🚧 Minor tweaks",
    "📝 Add temporary note",
    "🔍 Mark for review",
    "🧪 Testing changes",
    "🧹 Small cleanup"
]

# --- STEP 1: Modify the file ---
with open(file_path, "r") as f:
    lines = f.readlines()

line_idx = random.randint(0, len(lines) - 1)
insert_line = f"{possible_comments[random.randint(0, len(possible_comments)-1)]}  # added {datetime.now().strftime('%H:%M:%S')}\n"

lines.insert(line_idx, insert_line)

with open(file_path, "w") as f:
    f.writelines(lines)

print(f"🛠️ Inserted comment at line {line_idx + 1}: {insert_line.strip()}")

# --- STEP 2: Git add and commit ---
try:
    subprocess.run(["git", "add", file_path], check=True)
    msg = random.choice(commit_messages)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    print(f"✅ Committed with message: {msg}")
except subprocess.CalledProcessError as e:
    print(f"❌ Git error: {e}")
