"""Browser smoke check. Run: uv run --with playwright python tools/check-estate-preview.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/estate'
url='http://127.0.0.1:4321/world/blender/index.html?v=3'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
    page.emulate_media(reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.goto(url,wait_until='networkidle')
    page.locator('.pin').first.wait_for()
    assert page.locator('.pin').count()==6
    assert page.locator('.effect').count()==9
    assert page.locator('#effects').is_hidden()
    page.emulate_media(reduced_motion='no-preference')
    page.wait_for_function("document.querySelector('#motion').getAttribute('aria-pressed')==='true'")
    assert page.locator('#effects').is_visible()
    page.get_by_role('button',name='动效',exact=True).click()
    assert page.locator('#effects').is_hidden()
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('img.day').evaluate('(img)=>img.complete && img.naturalWidth===640')
    page.screenshot(path=str(out/'pixel-preview-desktop.png'),full_page=True)
    page.get_by_role('button',name='夜间',exact=True).click()
    page.wait_for_function("document.querySelector('img.night').complete && document.querySelector('img.night').naturalWidth===640")
    assert page.locator('img.night').is_visible()
    assert not page.locator('img.day').is_visible()
    page.screenshot(path=str(out/'pixel-preview-night.png'),full_page=True)
    page.get_by_role('button',name='对照第二版').click()
    page.wait_for_function("document.querySelector('img.night').complete && document.querySelector('img.night').naturalWidth===1440")
    assert page.locator('.scene').get_attribute('data-version')=='previous'
    page.get_by_role('button',name='对照第二版').click()
    page.get_by_role('button',name='地标',exact=True).click()
    assert not page.locator('.pin').first.is_visible()
    page.get_by_role('button',name='地标',exact=True).click()
    page.get_by_role('button',name='放大看细节').click()
    assert page.locator('.scene').evaluate('(e)=>Math.round(e.getBoundingClientRect().width)')==1280
    page.get_by_role('button',name='适应窗口').click()
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('button',name='日间',exact=True).click()
    page.wait_for_function("document.querySelector('img.day').complete && document.querySelector('img.day').naturalWidth===640")
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Mobile document overflow'
    page.screenshot(path=str(out/'pixel-preview-mobile.png'),full_page=True)
    page.get_by_role('button',name='放大看细节').click()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Zoom leaked outside scroller'
    assert page.locator('.viewport').evaluate('(e)=>e.scrollWidth>e.clientWidth')
    # Labels must remain tied to the same normalized camera positions on mobile.
    assert page.locator('.pin').count()==6
    assert not errors, errors
    browser.close()
    browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    page=browser.new_page(java_script_enabled=False,viewport={'width':390,'height':844})
    page.goto(url,wait_until='networkidle')
    assert page.locator('nav a').count()==6
    assert page.locator('img.day').is_visible()
    browser.close()
print('PREVIEW_OK: desktop, night, compare, labels, zoom, mobile overflow, no-JS navigation')
