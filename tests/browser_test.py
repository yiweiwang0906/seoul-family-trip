"""Functional acceptance checks on the GitHub Pages-style subpath."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'test-results'
OUT.mkdir(exist_ok=True)
URL = os.environ.get('TRIP_TEST_URL', 'http://127.0.0.1:8765/seoul-family-trip/')

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    response = page.goto(URL)
    assert response.status == 200
    page.wait_for_load_state('networkidle')
    expect(page.locator('.place-card')).to_have_count(17)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT / 'desktop-explore.png'), full_page=True)

    # Region, time, environment, stroller, duration, child and text filters.
    page.locator('[data-action="region-filter"][data-id="west"]').click()
    expect(page.locator('.place-card')).to_have_count(2)
    page.locator('[data-filter="time"]').select_option('晚上')
    expect(page.locator('.place-card')).to_have_count(1)
    page.locator('[data-action="clear-filters"]').click()
    page.locator('[data-filter="env"]').select_option('室内')
    expect(page.locator('.place-card')).to_have_count(4)
    page.locator('[data-filter="duration"]').select_option('short')
    expect(page.locator('.place-card')).to_have_count(2)
    page.locator('[data-filter="stroller"]').select_option('较友好')
    page.locator('[data-filter="kids"]').check()
    expect(page.locator('.place-card')).to_have_count(2)
    page.locator('[data-action="clear-filters"]').click()
    page.locator('[data-filter="search"]').fill('경복궁')
    expect(page.locator('.place-card')).to_have_count(1)
    page.locator('[data-action="fav"][data-id="palace"]').click()
    expect(page.locator('#saved-count')).to_have_text('1')
    page.locator('[data-action="detail"][data-id="palace"]').first.click()
    expect(page.locator('#detail-dialog')).to_be_visible()
    expect(page.locator('#detail-dialog')).to_contain_text('勤政殿月台')
    assert 'map.naver.com' in page.locator('#detail-dialog a').first.get_attribute('href')
    page.locator('#detail-dialog [data-action="add"]').click()
    form = page.locator('#entry-form')
    form.locator('[name="date"]').select_option('2026-10-03')
    form.locator('[name="slot"]').select_option('晚上')
    form.locator('[name="time"]').fill('19:00')
    expect(page.locator('#entry-preview')).to_contain_text('不在已公布')
    form.locator('[name="note"]').fill('<img src=x onerror=alert(1)> 家庭合影')
    form.locator('button[type="submit"]').click()
    assert page.evaluate('JSON.parse(localStorage.getItem("seoul-family-notes-v1")).entries.length') == 1, page.locator('#toast').inner_text() + str(errors)
    page.locator('nav a[href="#plan"]').click()
    expect(page.locator('.plan-item')).to_have_count(1)
    expect(page.locator('.plan-item')).to_contain_text('<img src=x')
    expect(page.locator('.plan-item img')).to_have_count(0)

    # Edit, move dates and preserve duration/note. Conflict with nap.
    page.locator('.plan-item [data-action="edit"]').click()
    form.locator('[name="date"]').select_option('2026-10-04')
    form.locator('[name="slot"]').select_option('下午')
    form.locator('[name="time"]').fill('14:00')
    form.locator('button[type="submit"]').click()
    expect(page.locator('.plan-item')).to_contain_text('与酒店午休重叠')
    page.locator('#nap-form [name="start"]').fill('12:00')
    page.locator('#nap-form [name="end"]').fill('13:00')
    page.locator('#nap-form button[type="submit"]').click()
    expect(page.locator('.plan-item')).not_to_contain_text('与酒店午休重叠')

    # Second event: overlap and reorder; add a Monday-closed place.
    page.locator('[data-action="add-any"][data-slot="下午"]').click()
    form.locator('[name="id"]').select_option('namsan')
    form.locator('[name="time"]').fill('14:30')
    form.locator('button[type="submit"]').click()
    expect(page.locator('.plan-item')).to_have_count(2)
    expect(page.locator('.plan-item').first).to_contain_text('时间重叠')
    page.locator('.plan-item').nth(1).locator('[data-action="up"]').click()
    expect(page.locator('.plan-item').first.locator('h4')).to_contain_text('南山')
    page.locator('.plan-item').first.locator('[data-action="down"]').click()
    expect(page.locator('.plan-item').first.locator('h4')).to_contain_text('景福宫')
    page.locator('[data-action="add-any"][data-slot="上午"]').click()
    form.locator('[name="id"]').select_option('diki')
    form.locator('[name="date"]').select_option('2026-10-05')
    form.locator('[name="time"]').fill('10:30')
    expect(page.locator('#entry-preview')).to_contain_text('常规闭馆')
    form.locator('button[type="submit"]').click()
    expect(page.locator('.plan-item')).to_contain_text('常规闭馆')
    page.reload()
    page.wait_for_load_state('networkidle')
    page.locator('[data-action="date"][data-id="2026-10-05"]').click()
    expect(page.locator('.plan-item')).to_have_count(1)
    page.locator('[data-action="date"][data-id="2026-10-06"]').click()
    expect(page.locator('#day-plan')).to_contain_text('返程日')
    expect(page.locator('.slot')).to_have_count(0)

    # Checklist and food/photo bookmarking, then file round trip.
    page.locator('nav a[href="#prepare"]').click()
    page.locator('[data-check="0"]').check()
    expect(page.locator('#check-count')).to_contain_text('1 /')
    page.locator('nav a[href="#food"]').click()
    page.locator('[data-action="food-filter"][data-id="早餐"]').click()
    expect(page.locator('.food-card')).to_have_count(3)
    page.locator('[data-action="fav"][data-id="tous"]').click()
    page.locator('[data-action="food-filter"][data-id="四格照"]').click()
    expect(page.locator('.photo-panel')).to_have_count(2)
    page.locator('[data-action="fav"][data-id="photoH"]').click()
    page.locator('nav a[href="#plan"]').click()
    with page.expect_download() as download:
        page.locator('[data-action="export"]').click()
    file = OUT / 'roundtrip.json'
    download.value.save_as(str(file))
    exported = json.loads(file.read_text('utf-8'))
    assert len(exported['entries']) == 3
    assert len(exported['favorites']) == 3
    assert exported['checks'] == [0]
    page.locator('[data-action="reset-plan"]').click()
    page.locator('#confirm-yes').click()
    assert page.evaluate('JSON.parse(localStorage.getItem("seoul-family-notes-v1")).entries.length') == 0
    # Cancel a valid import: state must remain unchanged.
    page.locator('#import-file').set_input_files(str(file))
    expect(page.locator('#confirm-dialog')).to_be_visible()
    page.locator('#confirm-dialog [data-action="close"]').last.click()
    assert page.evaluate('JSON.parse(localStorage.getItem("seoul-family-notes-v1")).entries.length') == 0
    page.locator('#import-file').set_input_files([])
    page.locator('#import-file').set_input_files(str(file))
    page.locator('#confirm-yes').click()
    assert page.evaluate('JSON.parse(localStorage.getItem("seoul-family-notes-v1")).entries.length') == 3
    bad = OUT / 'invalid.json'
    invalid = dict(exported)
    invalid['entries'] = [{'uid': 'bad', 'id': 'unknown'}]
    bad.write_text(json.dumps(invalid), encoding='utf-8')
    page.locator('#import-file').set_input_files(str(bad))
    expect(page.locator('#toast')).to_contain_text('未导入')
    assert page.evaluate('JSON.parse(localStorage.getItem("seoul-family-notes-v1")).entries.length') == 3

    # Map keyboard interaction, weather timestamp, tickets, all pages on mobile.
    page.locator('nav a[href="#map"]').click()
    page.locator('.map-node[data-id="west"]').focus()
    page.keyboard.press('Enter')
    expect(page.locator('#region-title')).to_contain_text('弘大')
    page.locator('nav a[href="#booking"]').click()
    expect(page.locator('.ticket-card')).to_have_count(8)
    page.locator('nav a[href="#weather"]').click()
    expect(page.locator('.weather-card')).to_have_count(5)
    expect(page.locator('main')).to_contain_text('2026/9/27 06:00')
    page.set_viewport_size({'width': 390, 'height': 844})
    for route in ['explore', 'map', 'plan', 'food', 'booking', 'weather', 'prepare']:
        page.goto(URL + '#' + route)
        page.wait_for_load_state('networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), route
        if route in ['explore', 'plan', 'weather']:
            page.screenshot(path=str(OUT / f'mobile-{route}.png'), full_page=True)
    # Reset explorer filters to showcase all cards.
    page.goto(URL + '#explore')
    page.locator('[data-action="clear-filters"]').click()
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(OUT / 'mobile-home.png'), full_page=True)
    page.locator('[data-action="detail"][data-id="namsan"]').first.click()
    assert page.locator('#detail-dialog').evaluate('(el)=>el.scrollWidth<=el.clientWidth')
    page.screenshot(path=str(OUT / 'mobile-detail.png'))
    page.locator('#detail-dialog [data-action="close"]').click()
    # Print content has all dates and protects escaped notes.
    page.evaluate('window.print=()=>{}')
    page.locator('footer [data-action="print"]').click()
    expect(page.locator('#print-root')).to_contain_text('10/6')
    expect(page.locator('#print-root img')).to_have_count(0)
    page.emulate_media(media='print')
    page.pdf(path=str(OUT / 'travel-guide.pdf'), format='A4', print_background=True)
    page.emulate_media(media='screen')

    # A full offline reload on project subpath, not merely a cached DOM.
    page.evaluate('navigator.serviceWorker.ready')
    page.wait_for_function('navigator.serviceWorker.controller !== null')
    context.set_offline(True)
    page.goto(URL + '#food')
    page.reload()
    expect(page.locator('main h1')).to_contain_text('好好吃饭')
    page.goto(URL + '#plan')
    page.reload()
    expect(page.locator('main h1')).to_contain_text('把喜欢的')
    context.set_offline(False)
    assert not errors, errors
    print(json.dumps({'result': 'PASS', 'checks': ['17 attraction cards and all filters', 'favorites and reload persistence', 'time/nap/closure warnings', 'edit/move/reorder', 'return day protection', 'food and photo cards', 'checklist', 'export/import/cancel/invalid file', 'escaped notes', 'keyboard map', '7 mobile pages without horizontal overflow', 'print PDF', 'offline full reload on Pages subpath', 'no browser errors'], 'artifacts': str(OUT)}, ensure_ascii=False, indent=2))
    browser.close()
