from pathlib import Path
import os
import subprocess
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:
    framework_python = '/Library/Frameworks/Python.framework/Versions/3.13/bin/python3'
    if sys.executable != framework_python and Path(framework_python).exists():
        os.execv(framework_python, [framework_python, __file__])
    raise

ROOT = Path(__file__).parent
URL = 'http://127.0.0.1:8770/index.html'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def metrics(page):
    return page.evaluate("""() => ({
      width: innerWidth,
      height: innerHeight,
      scrollWidth: document.documentElement.scrollWidth,
      oversized: [...document.querySelectorAll('body *')].filter(el => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return s.display !== 'none' && r.width > innerWidth + 2;
      }).map(el => `${el.tagName}.${el.className}`).slice(0, 10)
    })""")


def assert_layout(page, name):
    result = metrics(page)
    assert result['width'] == 1440 and result['height'] == 900, (name, result)
    assert result['scrollWidth'] <= 1440, (name, result)
    assert not result['oversized'], (name, result)
    return result


server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '8770', '--directory', str(ROOT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
time.sleep(0.7)
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
        page = browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        page.set_default_timeout(5000)
        page.goto(URL, wait_until='networkidle')

        nav = page.locator('button.nav[data-view]').all_inner_texts()
        assert nav == ['首页\n4', '任务\n6', '历史'], nav
        assert page.locator('.nav[data-view="canvas"], .nav[data-view="review"]').count() == 0
        assert page.locator('.view[data-view="home"].active').count() == 1
        assert '需要你处理' in page.locator('.view[data-view="home"]').inner_text()
        home = assert_layout(page, 'home')
        page.screenshot(path=str(ROOT / '01-home.png'), full_page=False)

        page.locator('button.nav[data-view="tasks"]').click()
        assert page.locator('.view[data-view="tasks"].active').count() == 1
        assert page.locator('.task-record').count() >= 6
        page.locator('[data-filter-group="tasks"] button[data-filter="user"]').click()
        assert page.locator('.task-record:not([hidden])').count() == 2
        page.locator('[data-filter-group="tasks"] button[data-filter="all"]').click()
        tasks = assert_layout(page, 'tasks')
        page.screenshot(path=str(ROOT / '02-tasks.png'), full_page=False)

        page.locator('.task-record[data-open-task]').click()
        assert page.locator('.view[data-view="canvas"].active').count() == 1
        assert page.locator('.canvas-field .node').count() == 6
        assert page.locator('.view[data-view="canvas"] .wb-tabs button').all_inner_texts() == ['Plan', 'Browser', 'Files', 'Documents']
        page.locator('.view[data-view="canvas"] .wb-tabs button[data-pane="files"]').click()
        assert page.locator('.view[data-view="canvas"] .wb-pane[data-pane="files"].active').count() == 1
        canvas = assert_layout(page, 'canvas')
        page.screenshot(path=str(ROOT / '04-task-canvas.png'), full_page=False)
        page.locator('.view[data-view="canvas"] [data-back="tasks"]').click()
        assert page.locator('.view[data-view="tasks"].active').count() == 1

        page.locator('button.nav[data-view="history"]').click()
        assert page.locator('.view[data-view="history"].active').count() == 1
        assert page.locator('.history-record').count() >= 5
        page.locator('[data-filter-group="history"] button[data-filter="accepted"]').click()
        assert page.locator('.history-record:not([hidden])').count() == 2
        page.locator('[data-filter-group="history"] button[data-filter="all"]').click()
        history = assert_layout(page, 'history')
        page.screenshot(path=str(ROOT / '03-history.png'), full_page=False)

        page.locator('.history-record[data-review-result]').first.click()
        assert page.locator('.view[data-view="review"].active').count() == 1
        assert 'Evidence' in page.locator('.view[data-view="review"]').inner_text()
        assert page.locator('.view[data-view="review"] .wb-tabs button').all_inner_texts() == ['Plan', 'Browser', 'Files', 'Documents']
        page.locator('.view[data-view="review"] .wb-tabs button[data-pane="documents"]').click()
        assert page.locator('.view[data-view="review"] .wb-pane[data-pane="documents"].active').count() == 1
        review = assert_layout(page, 'review')
        page.screenshot(path=str(ROOT / '05-result-review.png'), full_page=False)

        page.locator('#continueTask').click()
        assert page.locator('.view[data-view="canvas"].active').count() == 1
        page.evaluate("window.peerPrototype.showView('review')")
        page.locator('#acceptResult').click()
        page.wait_for_timeout(650)
        assert page.locator('.view[data-view="history"].active').count() == 1

        print({'home': home, 'tasks': tasks, 'history': history, 'canvas': canvas, 'review': review})
        print('five views, filters, detail flow and Workbench: PASS')
        browser.close()
finally:
    server.terminate()
    try:
        server.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server.kill()
