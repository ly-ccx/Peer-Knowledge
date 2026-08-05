from pathlib import Path
import os, subprocess, sys, time
try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:
    py='/Library/Frameworks/Python.framework/Versions/3.13/bin/python3'
    if sys.executable!=py and Path(py).exists(): os.execv(py,[py,__file__])
    raise
ROOT=Path(__file__).parent
URL='http://127.0.0.1:8790/index.html'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def layout(page,name):
    m=page.evaluate("""() => ({w:innerWidth,h:innerHeight,sw:document.documentElement.scrollWidth,bad:[...document.querySelectorAll('.page.active *')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return s.display!=='none'&&(r.right>innerWidth+2||r.left<-2)}).slice(0,8).map(e=>e.className||e.tagName)})""")
    assert m['w']==1440 and m['h']==900,(name,m)
    assert m['sw']<=1440 and not m['bad'],(name,m)
    return m

server=subprocess.Popen([sys.executable,'-m','http.server','8790','--directory',str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(.7)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path=CHROME)
    page=b.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
    page.set_default_timeout(5000);page.goto(URL,wait_until='networkidle')
    results={}
    assert page.locator('.action-row:not(.resolved)').count()==3
    results['home']=layout(page,'home');page.screenshot(path=str(ROOT/'01-action-inbox.png'))
    page.locator('#approveDecision').click();assert page.locator('.action-row:not(.resolved)').count()==2
    assert page.locator('#homeCount').inner_text()=='2'
    page.locator('[data-view-target="tasks"]').first.click();assert page.locator('.page[data-page="tasks"].active').count()==1
    results['tasks']=layout(page,'tasks');page.screenshot(path=str(ROOT/'02-task-index.png'))
    page.locator('.task-row [data-open-task]').first.click();assert page.locator('.page[data-page="task"].active').count()==1
    assert page.locator('#decisionStatus').inner_text().startswith('已批准')
    assert page.locator('[data-workbench-tab]').all_inner_texts()==['☷\nPlan','◎\nBrowser','▤\nFiles','▧\nDocuments']
    results['task']=layout(page,'task');page.screenshot(path=str(ROOT/'07-task-canvas.png'))
    page.locator('[data-task-mode="run"]').click();page.locator('#openComputerUse').click()
    assert page.locator('.page[data-page="computer-use"].active').count()==1
    results['computer']=layout(page,'computer');page.screenshot(path=str(ROOT/'08-computer-use.png'))
    page.locator('#completeComputerUse').click();assert page.evaluate('peer3.state.evidence')
    page.evaluate("peer3.showView('home')");page.locator('.page[data-page="home"] [data-open-automation]').click()
    results['automation']=layout(page,'automation');page.screenshot(path=str(ROOT/'04-automation.png'))
    page.locator('#grantPermission').click();assert page.evaluate('peer3.state.permission')
    page.evaluate("peer3.showView('home')");assert page.locator('.action-row:not(.resolved)').count()==1
    page.locator('.page[data-page="home"] [data-open-result]').click();results['result']=layout(page,'result');page.screenshot(path=str(ROOT/'09-result-package.png'))
    page.locator('#acceptResult').click();page.wait_for_timeout(750)
    assert page.locator('.page[data-page="cognition"].active').count()==1
    assert page.locator('[data-cognition-panel="changes"].active').count()==1
    assert page.locator('#homeCount').inner_text()=='0'
    page.locator('#acceptCognition').click();assert page.locator('#memoryBadge').inner_text()=='13'
    page.locator('[data-cognition-tab="graph"]').first.click();results['cognition']=layout(page,'cognition');page.screenshot(path=str(ROOT/'03-project-cognition.png'))
    page.locator('[data-view-target="skills"]').click();results['skills']=layout(page,'skills');page.screenshot(path=str(ROOT/'05-skills.png'))
    page.locator('#approvePatch').click();assert page.evaluate('peer3.state.patch')
    page.evaluate("peer3.openCognitionTab('memory')");results['memory']=layout(page,'memory');page.screenshot(path=str(ROOT/'06-memory.png'))
    assert all(not v['bad'] for v in results.values())
    print(results);print('three loops, shared state and 1440x900 layout: PASS')
    b.close()
finally:
  server.terminate()
  try: server.wait(timeout=2)
  except subprocess.TimeoutExpired: server.kill()
