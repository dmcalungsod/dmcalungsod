import json
import re
import urllib.request

ORCID_ID = "0009-0007-5571-7956"
URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
README_PATH = "README.md"

START_MARKER = "<!-- ORCID-WORKS:START -->"
END_MARKER = "<!-- ORCID-WORKS:END -->"

def main():
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        },
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to fetch ORCID data: {e}")
        return

    groups = data.get("group", [])
    
    markdown_lines = []
    
    if not groups:
        markdown_lines.append("*No publications yet, but working on it!*")
    else:
        # Sort groups by year descending if possible, ORCID usually returns them sorted but just in case
        for group in groups[:5]:
            # ORCID groups multiple versions of a work, we take the first summary
            summaries = group.get("work-summary", [])
            if not summaries:
                continue
            
            work = summaries[0]
            
            title = work.get("title", {}).get("title", {}).get("value", "Untitled")
            
            # Try to get the year
            year = "N/A"
            pub_date = work.get("publication-date")
            if pub_date and pub_date.get("year"):
                year = pub_date["year"].get("value", "N/A")
                
            # Try to get journal title
            journal = work.get("journal-title", {}).get("value") if work.get("journal-title") else None
            
            # Try to get DOI URL
            url = None
            if work.get("url") and work.get("url").get("value"):
                url = work["url"]["value"]
            else:
                ext_ids = work.get("external-ids", {}).get("external-id", [])
                for ext_id in ext_ids:
                    if ext_id.get("external-id-type") == "doi":
                        doi_val = ext_id.get("external-id-value")
                        if doi_val:
                            url = f"https://doi.org/{doi_val}"
                            break
            
            # Format the output
            entry = f"- **{title}** ({year})"
            if journal:
                entry += f" — *{journal}*"
            if url:
                entry += f" [[Link]({url})]"
                
            markdown_lines.append(entry)
            
        markdown_lines.append("")
        markdown_lines.append(f"*[See all my publications on ORCID ↗](https://orcid.org/{ORCID_ID})*")

    new_content = "\n".join(markdown_lines) + "\n"

    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme = f.read()
    except FileNotFoundError:
        print(f"{README_PATH} not found.")
        return

    pattern = f"({re.escape(START_MARKER)}\n).*?(\n{re.escape(END_MARKER)})"
    
    # If markers don't exist, we just exit cleanly (or we could append, but exiting is safer)
    if not re.search(pattern, readme, re.DOTALL):
        print("Markers not found in README.md. Please add them.")
        return

    updated_readme = re.sub(
        pattern,
        f"\\1{new_content}\\2",
        readme,
        flags=re.DOTALL,
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_readme)
        
    print("README.md updated successfully with ORCID works!")

if __name__ == "__main__":
    main()
