import asyncio
from playwright.async_api import async_playwright
import os

async def run_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        file_path = "file://" + os.path.abspath("src/python/bridge/dashboards/static/index.html")
        await page.goto(file_path)

        # Mock React mounting by adding a child to #root
        await page.evaluate("document.getElementById('root').innerHTML = '<div>Mock React Content</div>'")

        # Wait for the script to run
        await asyncio.sleep(1)

        panel = await page.query_selector(".trades-panel")
        if panel:
            print("✅ Trades panel found in index.html after mock mount")
            await page.screenshot(path="web_dashboard_trades.png")
            print("Screenshot saved to web_dashboard_trades.png")
        else:
            print("❌ Trades panel NOT found in index.html")
            content = await page.content()
            with open("page_debug.html", "w") as f:
                f.write(content)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
