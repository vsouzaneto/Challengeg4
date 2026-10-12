# Teste da ferramenta nos dois cenários (rode dentro desta pasta): python test_dashboard.py
# Requer: pip install playwright && playwright install chromium
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':1600})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+__import__('os').path.abspath('index.html')); await pg.wait_for_timeout(500)
        print('VERDICT default:', await pg.text_content('#verdict')); print('locked:', await pg.evaluate("document.getElementById('perf-card').classList.contains('locked')"))
        await pg.screenshot(path='screenshot_dataset_kaggle.png', full_page=True)
        await pg.set_input_files('#file','tests/real_like_sample.csv'); await pg.wait_for_timeout(4000)
        print('VERDICT real-like:', await pg.text_content('#verdict')); print('locked:', await pg.evaluate("document.getElementById('perf-card').classList.contains('locked')"))
        print(await pg.text_content('#kpis'))
        await pg.screenshot(path='screenshot_csv_com_sinal.png', full_page=True)
        print('errors:',errs); await b.close()
asyncio.run(main())
