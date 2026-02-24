from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501")

    # Wait for the sidebar to load and check if "Bearer Token" is present
    try:
        # Streamlit sidebar is usually an iframe or just a div, but selectors can be tricky.
        # We can look for text.
        page.wait_for_selector('text="Bearer Token (API Oficial)"', timeout=15000)
        print("Found Bearer Token input!")

        # Take screenshot
        page.screenshot(path="/home/jules/verification/streamlit_screenshot.png")
    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="/home/jules/verification/error_screenshot.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
