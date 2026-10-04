from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent
url = 'http://127.0.0.1:4321/world/'
# Coordinates are the visible printed labels in the approved image, not link centers.
labels = {
    'home': (398, 806, '/'), 'blog': (914, 255, '/blog/'),
    'chores': (313, 609, '/chores/'), 'making': (338, 442, '/chores/making/'),
    'garden': (460, 213, '/chores/garden/'), 'about': (1398, 279, '/about/'),
    'friends': (166, 865, '/friend/'), 'backyard': (1288, 593, '/backyard/'),
}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    page = browser.new_page()
    page.emulate_media(reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    for name, width, height in [('desktop', 1440, 900), ('mobile', 390, 844), ('landscape', 844, 390)]:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(url, wait_until='networkidle')
        page.wait_for_function('document.querySelector(".estate-map").complete && document.querySelector(".estate-map").naturalWidth === 1536')
        assert page.locator('.room-hit').count() == 8
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
        bounds = page.locator('.estate-map').bounding_box()
        assert abs(bounds['width'] / bounds['height'] - 1.5) < .01
        assert bounds['x'] >= 0 and bounds['x'] + bounds['width'] <= width + 1
        for room, (x, y, href) in labels.items():
            px = bounds['x'] + x / 1536 * bounds['width']
            py = bounds['y'] + y / 1024 * bounds['height']
            hit = page.evaluate('([x,y]) => document.elementFromPoint(x,y)?.closest("a")?.getAttribute("href")', [px, py])
            assert hit == href, (name, room, hit, href)
        page.screenshot(path=str(out / f'garden-{name}.png'), full_page=True)
        if name == 'mobile':
            assert page.locator('.world-mobile-nav').is_visible()
            for link in page.locator('.world-mobile-nav a').all():
                assert link.bounding_box()['height'] >= 44
        page.locator('.room-hit--blog').focus()
        assert page.locator('.room-hit--blog').evaluate('(e) => e.matches(":focus-visible")')
        page.get_by_role('button', name='Toggle theme').click()
        assert page.locator('.estate-map').is_visible()
    # Exercise an actual pointer navigation from a printed label on the map.
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(url, wait_until='networkidle')
    bounds = page.locator('.estate-map').bounding_box()
    page.mouse.click(bounds['x'] + 1398 / 1536 * bounds['width'], bounds['y'] + 279 / 1024 * bounds['height'])
    page.wait_for_url('**/about/')
    page.goto(url, wait_until='networkidle')
    page.locator('.room-hit--backyard').focus()
    page.keyboard.press('Enter')
    page.wait_for_url('**/backyard/')
    assert not errors, errors
    context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
    offline_page = context.new_page()
    offline_page.goto(url, wait_until='networkidle')
    assert offline_page.locator('.world-mobile-nav a').count() == 8
    offline_page.bring_to_front()
    target = offline_page.locator('.world-mobile-nav a[href="/about/"]')
    target_box = target.bounding_box()
    offline_page.mouse.click(target_box['x'] + target_box['width'] / 2, target_box['y'] + target_box['height'] / 2)
    offline_page.wait_for_url('**/about/')
    browser.close()
print('PASS: visible-label alignment for all 8 links at 3 viewport sizes; mobile targets; theme; keyboard and pointer navigation; no-JS navigation; no browser errors.')
