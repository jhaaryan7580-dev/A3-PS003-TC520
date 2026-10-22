"""Optional real-browser integration checks; not training or statistical evaluation.
Install playwright separately and use system Chromium. Run the compiled local lab first.
No NPZ is distributed. --dataset selects the exact user-owned local benchmark.
"""
from pathlib import Path
import argparse,json,re,math
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:3000')
parser.add_argument('--dataset',required=True)
parser.add_argument('--out',required=True)
parser.add_argument('--chromium',default='/usr/bin/chromium')
parser.add_argument('--allow-manus-host-telemetry',action='store_true',help='Only for the published Manus origin: report three observed platform telemetry endpoints separately; all other POSTs still fail.')
args=parser.parse_args()
checks=[]; errors=[]; posts=[]
known_platform_posts={
    ('api.manus.im','/api/user_behavior/batch_create_event_v2'),
    ('api2.amplitude.com','/2/httpapi'),
    ('manus-analytics.com','/api/send'),
}
if args.allow_manus_host_telemetry:
    assert urlparse(args.url).netloc=='chaurahalab-gzh27d5b.manus.space', 'Telemetry allowance is restricted to the verified published origin'
def record_post(r):
    if r.method!='POST':return
    u=urlparse(r.url)
    size=len(r.post_data_buffer or b'')
    allowed=args.allow_manus_host_telemetry and u.scheme=='https' and (u.netloc,u.path) in known_platform_posts and size<65536
    posts.append({'host':u.netloc,'path':u.path,'method':r.method,'resource_type':r.resource_type,'body_bytes':size,'classification':'hosting telemetry' if allowed else 'unexpected POST'})
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',record_post)
 page.goto(args.url,wait_until='networkidle')
 page.get_by_role('heading',name='Forecast laboratory',exact=True).wait_for()
 page.get_by_role('button',name='Run forward pass',exact=True).click()
 table=page.get_by_role('table',name='Same-window forecast comparison')
 table.wait_for()
 check('Manual inference compares three predictors without invented truth',table.locator('tbody tr').count()==3 and table.inner_text().count('No truth in manual mode')==3)
 page.locator('#history').fill('0, 166, 173, 170, 168, 172, 175, 178, 180, 176, 179, 181')
 page.get_by_role('button',name='Run forward pass',exact=True).click()
 check('Zero manual input rejected and old receipt cleared',page.locator('.note-warning').count()>0 and page.get_by_role('table',name='Same-window forecast comparison').count()==0)
 page.locator('input[type=file]').set_input_files(args.dataset)
 page.get_by_text('Verified PEMS08 · held-out playback',exact=True).wait_for()
 page.wait_for_function("document.querySelector('#history').value.startsWith('200, 170')")
 page.get_by_role('button',name='Run forward pass',exact=True).click()
 table=page.get_by_role('table',name='Same-window forecast comparison');table.wait_for()
 fed_row=table.locator('tbody tr').filter(has_text='Non-IID FedAvg')
 check('Held-out FedAvg inference matches fixed NumPy reference to displayed precision',abs(float(fed_row.locator('td').nth(1).inner_text().replace(',',''))-186.37592180221702)<0.001)
 page.get_by_role('button',name='Compare 12 target slots',exact=True).click()
 trace=page.get_by_role('table',name='Illustrative trace metrics');trace.wait_for()
 check('Contiguous illustration computes three local score rows',trace.locator('tbody tr').count()==3 and '12 / 12' in trace.inner_text())
 page.locator('#sensor').fill('170')
 page.wait_for_function("document.querySelector('.note-warning')?.textContent.includes('Sensor')")
 check('Out-of-range sensor does not crash or keep a stale comparison',page.get_by_role('heading',name='Forecast laboratory',exact=True).count()==1 and page.get_by_role('table',name='Same-window forecast comparison').count()==0)
 page.locator('#sensor').fill('156')
 page.wait_for_function("!document.querySelector('.note-warning')")
 page.get_by_role('button',name='Run forward pass',exact=True).click()
 check('Valid sensor recovers real inference',page.get_by_role('table',name='Same-window forecast comparison').count()==1)
 page.locator('input[type=file]').set_input_files({'name':'wrong.npz','mimeType':'application/octet-stream','buffer':b'not the benchmark'})
 page.get_by_text(re.compile('Previous verified dataset remains active')).wait_for()
 check('Rejected replacement keeps explicit usable verified dataset',page.get_by_text('Verified PEMS08 · held-out playback',exact=True).count()==1 and page.get_by_role('button',name='Run forward pass',exact=True).is_enabled())
 page.get_by_role('button',name='Run forward pass',exact=True).click()
 check('Inference still works after rejected replacement',page.get_by_role('table',name='Same-window forecast comparison').count()==1)
 page.get_by_role('button',name=re.compile('Experiment evidence')).click()
 page.get_by_role('button',name='RMSE',exact=True).click()
 persistence=page.locator('.result-table tbody tr').filter(has_text='Persistence')
 check('Persistence is in RMSE comparison with frozen value', '24.451' in persistence.inner_text())
 page.get_by_label('Aggregate or individual seed').select_option('1')
 check('Deterministic persistence remains explicit under seed selector','24.451' in persistence.inner_text())
 page.get_by_role('button',name=re.compile('Federation lab')).click()
 page.get_by_label('Replay budget').select_option('diagnostic')
 page.get_by_label('Saved round').fill('100')
 page.get_by_label('Replay budget').select_option('primary')
 page.wait_for_function("document.querySelector('input[aria-label=\"Saved round\"]').value==='1'")
 check('100-to-30-round switch resets safely',page.get_by_role('heading',name='Five operators. One shared model.').count()==1)
 page.get_by_text('Mentor walkthrough: how one FedAvg round works',exact=True).click()
 check('Visible mentor pseudocode contains weighted aggregation and validation selection','global_parameters = sum((n_k / total_n)' in page.locator('.pseudocode-block').inner_text() and 'test windows once' in page.locator('.pseudocode-block').inner_text())
 check('Both matched validation histories and descriptive target are displayed',page.locator('.validation-target-note').count()==1 and 'same seed/budget' in page.locator('.convergence-chart').inner_text())
 page.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")
 page.get_by_role('button',name=re.compile('Copy commands')).click()
 page.get_by_role('status').filter(has_text='Clipboard unavailable').wait_for()
 check('Missing clipboard API produces useful fallback instead of crashing',page.get_by_role('status').filter(has_text='copy them manually').count()==1)
 page.get_by_role('button',name=re.compile('Forecast lab')).click()
 check('Verified dataset remains in memory across workspace navigation',page.get_by_text('Verified PEMS08 · held-out playback',exact=True).count()==1)
 page.get_by_role('button',name='Unload file and return to manual mode',exact=True).click()
 check('Unload returns to manual mode without old recorded truth',page.get_by_text('Manual-input mode',exact=True).count()==1 and page.get_by_role('table',name='Same-window forecast comparison').count()==0)
 page.set_viewport_size({'width':390,'height':844})
 page.wait_for_timeout(150)
 check('Narrow viewport does not force whole-page horizontal scrolling',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'))
 check('No unhandled browser errors',not errors)
 check('No unexpected or application-origin POST/upload requests; known hosting telemetry reported separately',not any(r['classification']=='unexpected POST' for r in posts))
 browser.close()
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'status':'PASS','url':args.url,'scope':'Real isolated Chromium UI checks; not training, city validation, performance experiment or certification. No raw dataset transfer observed; this is not a platform-wide privacy audit.','checks':checks,'unhandled_errors':errors,'post_requests':posts,'hosting_telemetry_allowed':args.allow_manus_host_telemetry},indent=2)+'\n')
print(f'PASS: {len(checks)} real-browser UI checks. Report: {out}')
