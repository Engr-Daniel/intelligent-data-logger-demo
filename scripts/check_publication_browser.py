from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json, argparse
parser=argparse.ArgumentParser()
parser.add_argument("--base-url",default="http://127.0.0.1:8503")
parser.add_argument("--browser",default=None)
args=parser.parse_args()
base=args.base_url.rstrip("/")
expect.set_options(timeout=60000)
out=Path('docs/images');out.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(**({'executable_path':args.browser} if args.browser else {}),headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];console=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
 page.goto(base+'/explorer/?scenario=grid_outage_islanding')
 expect(page.locator('#detail-title')).to_have_text('Grid outage / islanding')
 expect(page.locator('#outage-trace svg')).to_have_count(3)
 page.screenshot(path=str(out/'experiment-explorer.png'),full_page=False)
 for i in range(6):
  page.locator('.scenario-button').nth(i).click()
  expect(page.locator('.scenario-button').nth(i)).to_have_attribute('aria-pressed','true')
  assert page.locator('#detail-title').inner_text()
 page.locator('[data-milestone="5"]').click();expect(page.locator('.workflow-note')).to_contain_text('Resolve')
 for width in [1440,850,390,320]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('() => document.documentElement.scrollWidth<=innerWidth'),('demo overflow',width)
 page.set_viewport_size({'width':1440,'height':1000})
 page.goto(base+'/explorer/research.html')
 expect(page.locator('#research-results tbody tr')).to_have_count(4)
 expect(page.locator('#research-results')).to_contain_text('97.1%')
 expect(page.locator('#live-results')).to_contain_text('24/24 conversations completed')
 expect(page.locator('#live-results')).to_contain_text('0/24 strict JSON')
 page.set_viewport_size({'width':1440,'height':1360})
 page.screenshot(path=str(out/'research-explorer.png'),full_page=False)
 page.locator('#stress').select_option('severe');expect(page.locator('#research-results')).to_contain_text('90.0%')
 page.locator('#stress').select_option('moderate');expect(page.locator('#research-results')).to_contain_text('97.5%')
 for width in [1440,850,390,320]:
  page.set_viewport_size({'width':width,'height':1000})
  assert page.evaluate('() => document.documentElement.scrollWidth<=innerWidth'),('research overflow',width)
 page.screenshot(path='.venv/research-mobile.png',full_page=True)
 page.set_viewport_size({'width':1440,'height':1000})
 page.goto(base+'/')
 expect(page.locator('#chart path')).to_have_count(3)
 page.screenshot(path=str(out/'operational-dashboard.png'),full_page=True)
 assert not errors,errors
 assert not [e for e in console if 'Content Security Policy' in e or 'Refused' in e],console
 print('Browser PASS: six scenarios, deep links, outage trace, workflow, three stress levels, primary/post-hoc distinction, dashboard, 320–1440px layouts; no JS or CSP errors.')
 browser.close()
