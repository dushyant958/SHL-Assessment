from playwright.sync_api import sync_playwright
import json
import time
import os
import re

URLS_FILE = '../data/urls.json'
OUTPUT_TXT = '../data/assessments.txt'

TEST_TYPE_MAPPING = {
    'A': 'Ability & Aptitude',
    'B': 'Biodata & Situational Judgment',
    'C': 'Competencies',
    'D': 'Development & 360',
    'E': 'Assessment Exercises',
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations'
}

def setup_browser(playwright):
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    browser = playwright.chromium.launch(executable_path=brave_path, headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    return browser, context

def handle_banners(page):
    try:
        if page.locator('button:has-text("I understand and wish to continue")').is_visible(timeout=10000):
            page.locator('button:has-text("I understand and wish to continue")').click()
            time.sleep(3)
    except:
        pass
    try:
        if page.locator('button:has-text("Continue")').is_visible(timeout=5000):
            page.locator('button:has-text("Continue")').click()
            time.sleep(2)
    except:
        pass

def extract_from_detail(page):
    data = {}

    try:
        data['description'] = page.locator('h4:has-text("Description") + p').inner_text(timeout=60000).strip()
    except:
        data['description'] = "Not found"

    try:
        data['job_levels'] = page.locator('h4:has-text("Job levels") + p').inner_text(timeout=40000).strip()
    except:
        data['job_levels'] = "Not found"

    try:
        data['languages'] = page.locator('h4:has-text("Languages") + p').inner_text(timeout=40000).strip()
    except:
        data['languages'] = "Not found"

    try:
        length = page.locator('h4:has-text("Assessment length") + p').inner_text(timeout=40000).strip()
        mins = re.search(r'\d+', length)
        data['duration'] = f"{mins.group(0)} minutes" if mins else "Unknown"
    except:
        data['duration'] = "Unknown"

    return data

def format_entry(name, test_type_letters, desc, levels, langs, duration):
    full_types = " | ".join(TEST_TYPE_MAPPING.get(l.strip(), l.strip()) for l in test_type_letters.split())
    if not full_types:
        full_types = "Unknown"

    entry = f"{name}\n"
    entry += f"Test Type: {full_types}\n"
    entry += f"{desc}\n"
    entry += f"Job Levels: {levels}\n"
    entry += f"Languages: {langs}\n"
    entry += f"Duration: {duration}\n"
    entry += f"Remote Testing Available.\n\n"
    return entry

def main():
    if not os.path.exists(URLS_FILE):
        print("urls.json not found. Run collect_urls.py first.")
        return

    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    print(f"Loaded {len(items)} URLs. Starting content extraction...")

    with sync_playwright() as p:
        browser, context = setup_browser(p)
        page = context.new_page()

        output = ""

        for item in items:
            name = item['name']
            url = item['url']
            test_type_letters = item.get('test_type', 'K')

            print(f"Extracting: {name}")

            try:
                page.goto(url, timeout=90000)
                page.wait_for_load_state('networkidle', timeout=90000)
                time.sleep(6)
                handle_banners(page)

                details = extract_from_detail(page)

                formatted = format_entry(
                    name=name,
                    test_type_letters=test_type_letters,
                    desc=details['description'],
                    levels=details['job_levels'],
                    langs=details['languages'],
                    duration=details['duration']
                )
                output += formatted

            except Exception as e:
                print(f"Failed {name}: {e}")
                output += format_entry(name, test_type_letters, "Failed to load", "Failed", "Failed", "Failed")

        with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"\nAll done! Content saved to {OUTPUT_TXT}")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    main()