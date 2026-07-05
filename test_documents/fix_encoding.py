import re

path = "generate_docs.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Replace known unicode chars with ASCII equivalents
replacements = {
    "\u2014": "--",   # em-dash
    "\u2013": "-",    # en-dash
    "\u2018": "'",    # left single quote
    "\u2019": "'",    # right single quote
    "\u201c": '"',    # left double quote
    "\u201d": '"',    # right double quote
    "\u2026": "...",  # ellipsis
    "\u00b0": " deg", # degree symbol
    "\u00d7": "x",    # multiplication sign
}
for old, new in replacements.items():
    text = text.replace(old, new)

# Strip any remaining non-ASCII
text = re.sub(r'[^\x00-\x7e]', '', text)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed all non-ASCII characters.")
