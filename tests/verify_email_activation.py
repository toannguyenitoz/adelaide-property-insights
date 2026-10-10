import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def run_activation_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = "file:///" + os.path.abspath("index.html").replace("\\", "/")
        await page.goto(file_path, wait_until="domcontentloaded")

        # 1. Clear state
        await page.evaluate("() => { localStorage.clear(); if(window.updateUserUI) window.updateUserUI(); }")
        await page.wait_for_timeout(500)

        print("--- TEST 1: GUEST IS RESTRICTED ---")
        nav_btn = await page.inner_text("#navAuthBtn")
        print("Nav Button Text for guest:", nav_btn)
        assert "Đăng Ký" in nav_btn or "Đăng Nhập" in nav_btn

        # 2. Open register modal and register a new account
        print("--- TEST 2: REGISTER ACCOUNT AND RECEIVE ACTIVATION EMAIL ---")
        await page.click("#navAuthBtn")
        await page.wait_for_timeout(500)

        test_email = "new_investor_activate@adelaide-homes.com.au"
        test_name = "Nguyen Van Test"
        test_pass = "SecurePass2026"

        await page.fill("#authName", test_name)
        await page.fill("#authEmail", test_email)
        await page.fill("#authPassword", test_pass)
        await page.click("#authSubmitBtn")
        await page.wait_for_timeout(800)

        # 3. Check Pending Activation Screen
        pending_box = page.locator("#authPendingContainer")
        assert await pending_box.is_visible(), "Pending activation screen must be visible!"
        pending_email = await page.inner_text("#pendingEmailDisplay")
        print("Pending screen displayed for email:", pending_email)
        assert test_email in pending_email

        # 4. Check user cannot log in before activating!
        print("--- TEST 3: CANNOT LOGIN BEFORE ACTIVATION ---")
        # Try switching to login tab and logging in
        await page.evaluate("() => switchAuthTab('login')")
        await page.wait_for_timeout(400)
        await page.fill("#authEmail", test_email)
        await page.fill("#authPassword", test_pass)
        await page.click("#authSubmitBtn")
        await page.wait_for_timeout(800)

        # Should be blocked and redirected back to Pending Activation
        assert await pending_box.is_visible(), "Should be redirected back to pending activation because account is not activated!"
        print("Confirmed: Unactivated account CANNOT log in.")

        # 5. Open simulated email inbox and verify activation email content
        print("--- TEST 4: OPEN INBOX AND VERIFY ACTIVATION LINK ---")
        await page.click("#btnSimulateEmailInbox")
        await page.wait_for_timeout(600)

        email_modal = page.locator("#emailInboxModal")
        assert await email_modal.is_visible(), "Email inbox modal must be visible!"
        email_body = await page.inner_text("#simulatedEmailContent")
        print("Email contains activation header:", "Adelaide Property Insights" in email_body)
        assert "KÍCH HOẠT TÀI KHOẢN NGAY" in email_body

        # 6. Click Activate Account button inside Email
        print("--- TEST 5: CLICK ACTIVATE BUTTON INSIDE EMAIL ---")
        # Handle dialog alert
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
        activate_link = page.locator("#simulatedEmailContent a:has-text('KÍCH HOẠT TÀI KHOẢN NGAY')").first
        await activate_link.click()
        await page.wait_for_timeout(1000)

        # 7. Verify user is now activated and VIP permissions unlocked
        print("--- TEST 6: VERIFY ACCOUNT IS ACTIVATED AND UNLOCKED ---")
        nav_slot_text = await page.inner_text("#userNavSlot")
        print("Nav Slot text after activation:", nav_slot_text)
        assert test_name in nav_slot_text, "User name must now appear in nav slot"

        # Check download modal is unlocked
        await page.evaluate("() => openDownloadModal()")
        await page.wait_for_timeout(500)
        download_modal = page.locator("#downloadModal")
        assert await download_modal.is_visible(), "Download modal must be accessible after activation"
        btn_master_text = await page.inner_text("#modalBtnMaster")
        print("Download Master text for activated member:", btn_master_text)
        assert "Tải Báo Cáo Đầy Đủ (PDF)" in btn_master_text

        print("ALL EMAIL ACTIVATION TESTS PASSED 100% PERFECTLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_activation_test())
