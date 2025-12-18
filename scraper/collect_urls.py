from playwright.sync_api import sync_playwright
import json
import time
import os

URLS_FILE = '../data/urls.json'

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

def main():
    with sync_playwright() as p:
        browser, context = setup_browser(p)
        page = context.new_page()

        all_items = []
        start = 0
        while start < 384:  # 32 pages × 12
            url = f"https://www.shl.com/products/product-catalog/?type=1&start={start}"
            print(f"Collecting URLs from: {url}")
            page.goto(url, timeout=90000)
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            handle_banners(page)

            links = page.locator('a[href*="/products/product-catalog/view/"]').all()
            print(f"  Found {len(links)} links")

            for link in links:
                name = link.inner_text().strip()
                href = link.get_attribute('href')
                full_url = f"https://www.shl.com{href}"

                # Get test type letters from last column
                try:
                    test_type = link.locator('xpath=ancestor::tr/td[last()]').inner_text().strip()
                except:
                    test_type = "K"

                all_items.append({
                    "name": name,
                    "url": full_url,
                    "test_type": test_type
                })

            start += 12

        os.makedirs('../data', exist_ok=True)
        with open(URLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_items, f, indent=2, ensure_ascii=False)

        print(f"\nURL collection complete! Saved {len(all_items)} items to {URLS_FILE}")
        browser.close()

if __name__ == "__main__":
    main()