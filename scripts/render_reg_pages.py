"""Render the public SOS voter registration statistics pages in headless Chrome and save the rendered file tables (month -> file links)."""
import asyncio,json,re
from playwright.async_api import async_playwright
PAGES={'2022':'https://www.sos.nm.gov/sos-archive/voter-statistics-data-archive/2022-voter-statistics-data/',
       '2026':'https://www.sos.nm.gov/voting-and-elections/data-and-maps/voter-registration-statistics/2026-voter-registration-data/'}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True)
        out={}
        for y,u in PAGES.items():
            pg=await b.new_page()
            await pg.goto(u,wait_until='domcontentloaded',timeout=90000)
            try: await pg.wait_for_selector('.rf-table a',timeout=60000)
            except Exception as ex: print('no links yet',ex)
            await pg.wait_for_timeout(8000)
            html=await pg.content()
            open(f'/workspace/nm-election/raw/reg_page_rendered_{y}.html','w').write(html)
            links=await pg.eval_on_selector_all('.rf-table a',"els=>els.map(e=>({text:e.closest('tr')?e.closest('tr').innerText:e.innerText,href:e.href,month:(e.closest('.et_pb_code_inner')||{querySelector:()=>null}).querySelector('h4')?.innerText}))")
            out[y]=links
            print(y,len(links))
        json.dump(out,open('/workspace/nm-election/raw/reg_file_links.json','w'),indent=1)
        await b.close()
asyncio.run(main())
