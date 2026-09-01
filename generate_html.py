import json
import html
from pathlib import Path

BASE = Path(__file__).parent
HADITHS_FILE = BASE / "hadiths.json"
STATE_FILE = BASE / "state.json"
TEMPLATE_FILE = BASE / "templates" / "page.html"
OUTPUT_HTML = BASE / "output.html"
LATEST_FILE = BASE / "latest.json"

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()

def htmlize_text(text: str) -> str:
    text = normalize_text(text)
    text = html.escape(text)
    return text.replace("\n", "<br>")

# قراءة ملف الأحاديث
with open(HADITHS_FILE, "r", encoding="utf-8") as f:
    hadiths = json.load(f)

# قراءة state
with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)

last_index = state.get("last_index", -1)
next_index = (last_index + 1) % len(hadiths)

item = hadiths[next_index]

sayer = htmlize_text(item.get("sayer", ""))
hadith = htmlize_text(item.get("text", ""))
reference = htmlize_text(item.get("reference", ""))

# قراءة القالب
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

# استبدال المتغيرات
result = (
    template
    .replace("{{SAYER}}", sayer)
    .replace("{{HADITH}}", hadith)
    .replace("{{REFERENCE}}", reference)
)

# حفظ HTML الناتج
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(result)

# تحديث state
state["last_index"] = next_index
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

# حفظ آخر حديث
latest = {
    "index": next_index,
    "id": item.get("id"),
    "sayer": item.get("sayer"),
    "text": item.get("text"),
    "reference": item.get("reference")
}
with open(LATEST_FILE, "w", encoding="utf-8") as f:
    json.dump(latest, f, ensure_ascii=False, indent=2)

print("تم إنشاء output.html بنجاح")
print("Hadith ID:", item.get("id"))
print("Index:", next_index)
