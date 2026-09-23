import json
import re
import urllib.request

USERNAME = "dmcalungsod"
URL = f"https://www.credly.com/users/{USERNAME}/badges.json"
README_PATH = "README.md"

START_MARKER = "<!-- CREDLY-BADGES:START -->"
END_MARKER = "<!-- CREDLY-BADGES:END -->"


def main():
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    badges = data.get("data", [])
    if not badges:
        print("No badges found on Credly profile.")
        return

    badge_elements = []
    for item in badges:
        badge_id = item.get("id")
        template = item.get("badge_template", {})
        name = template.get("name") or "Credly Certification"
        img_url = (
            item.get("image_url")
            or template.get("image_url")
            or (template.get("image") or {}).get("url")
        )

        if badge_id and img_url:
            link = f"https://www.credly.com/badges/{badge_id}"
            # Keep anchor and img tags tight to prevent any browser underline artifacts
            badge_elements.append(
                f'<a href="{link}"><img src="{img_url}" alt="{name}" height="100" /></a>'
            )

    badges_html = (
        f"{START_MARKER}\n"
        f'<p align="left">\n  '
        + "&nbsp;&nbsp;\n  ".join(badge_elements)
        + f"\n</p>\n"
        f"{END_MARKER}"
    )

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL
    )

    if not pattern.search(content):
        print("Error: Could not find Credly markers in README.md.")
        return

    new_content = pattern.sub(badges_html, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated README.md with {len(badge_elements)} badges.")


if __name__ == "__main__":
    main()
