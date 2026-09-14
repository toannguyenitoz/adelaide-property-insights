import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('file:///d:/Looking%20for%20a%20home/reports/report_preview.html', wait_until='load')
        
        # In Chromium, header and footer MUST include standard HTML with style
        h = '<div style="font-size: 8px; color: #666; width: 100%; text-align: right; padding-right: 15mm;"><style>div { font-size: 8px; }</style><span>TOAN NGUYEN IT OZ</span></div>'
        f = '<div style="font-size: 8px; color: #888; width: 100%; display: flex; justify-content: space-between; padding: 0 15mm;"><style>div { font-size: 8px; }</style><span>Toan Nguyen IT OZ</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        
        try:
            pdf = await page.pdf(
                format='A4',
                print_background=True,
                display_header_footer=True,
                header_template=h,
                footer_template=f,
                margin={'top': '25mm', 'bottom': '25mm', 'left': '15mm', 'right': '15mm'}
            )
            print(f'Success with styled header/footer! {len(pdf)} bytes')
        except Exception as e:
            print(f'Failed: {e}')

        await browser.close()

asyncio.run(test())
