import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = "file:///" + os.path.abspath("index.html").replace("\\", "/")
        await page.goto(file_path, wait_until="domcontentloaded")
        
        # 1. Clear any local storage
        await page.evaluate("() => { localStorage.clear(); if(window.updateUserUI) window.updateUserUI(); }")
        await page.wait_for_timeout(500)
        
        print("--- TEST 1: GUEST RESTRICTION ---")
        # Check user is Guest
        nav_btn = await page.inner_text("#navAuthBtn")
        print("Nav Button Text for guest:", nav_btn)
        assert "Đăng Ký" in nav_btn or "Đăng Nhập" in nav_btn
        
        # Click download modal button in Hero
        btn_hero = page.locator("button:has-text('Tải 2 Báo Cáo PDF MỚI')").first
        await btn_hero.click()
        await page.wait_for_timeout(500)
        
        # Verify Auth Modal is opened with Registration active
        auth_modal = page.locator("#authModal")
        is_visible = await auth_modal.is_visible()
        print("Auth Modal visible after clicking hero download:", is_visible)
        assert is_visible, "Auth modal should be visible for guest"
        
        auth_title = await page.inner_text("#authModalTitle")
        print("Auth Modal Title:", auth_title)
        assert "Đăng Ký" in auth_title, "Should default to Register tab"
        
        # Close auth modal
        close_btn = page.locator("#authModal button[onclick='closeAuthModal()']").first
        await close_btn.click()
        await page.wait_for_timeout(300)
        
        # Try clicking October report download button
        btn_october = page.locator("button:has-text('Tải Báo Cáo Tháng 10 PDF')").first
        await btn_october.click()
        await page.wait_for_timeout(500)
        is_visible_oct = await auth_modal.is_visible()
        print("Auth Modal visible after clicking October download:", is_visible_oct)
        assert is_visible_oct, "Auth modal should be visible when trying to download October report"
        
        # Close auth modal
        await close_btn.click()
        await page.wait_for_timeout(300)
        
        print("--- TEST 2: REGISTRATION & UNLOCK ---")
        # Open Auth Modal
        await page.click("#navAuthBtn")
        await page.wait_for_timeout(500)
        
        # Fill registration form
        test_email = "investor_vip_test@adelaide-homes.com.au"
        test_name = "Adelaide Investor VIP"
        test_pass = "SecurePass123"
        
        await page.fill("#authName", test_name)
        await page.fill("#authEmail", test_email)
        await page.fill("#authPassword", test_pass)
        
        # Submit registration
        await page.click("#authSubmitBtn")
        await page.wait_for_timeout(1000)
        
        # Verify user is now logged in
        nav_slot_text = await page.inner_text("#userNavSlot")
        print("User Display after registration:", nav_slot_text)
        assert test_name in nav_slot_text, "Should display registered user name"
        
        # Open Download Modal directly
        await page.evaluate("() => openDownloadModal()")
        await page.wait_for_timeout(500)
        
        download_modal = page.locator("#downloadModal")
        print("Download Modal visible:", await download_modal.is_visible())
        assert await download_modal.is_visible()
        
        # Check download buttons in modal are now active
        btn_master_text = await page.inner_text("#modalBtnMaster")
        print("Master download button text for member:", btn_master_text)
        assert "Tải Báo Cáo Đầy Đủ (PDF)" in btn_master_text
        
        print("--- TEST 3: ATTEMPTING EXECUTE DOWNLOAD AS GUEST IS BLOCKED ---")
        # Simulate logout
        await page.evaluate("() => logoutUser()")
        await page.wait_for_timeout(500)
        
        # If guest tries to execute download directly via JS
        await page.evaluate("() => executeDownload('master')")
        await page.wait_for_timeout(500)
        assert await auth_modal.is_visible(), "Executing download as guest must pop up auth modal!"
        msg_text = await page.inner_text("#authMsgBox")
        print("Auth error message displayed:", msg_text)
        assert "vui lòng đăng ký" in msg_text.lower() or "đăng ký" in msg_text.lower()
        
        print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
