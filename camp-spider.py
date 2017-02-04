import time
import os
from splinter import Browser
from selenium import webdriver

print os.environ.get('PATH')
chromedriver_root_path = '/usr/local/bin'
os.environ["PATH"] += os.pathsep + chromedriver_root_path
print os.environ.get('PATH')

# base_url = 'https://www.recreation.gov'
# srch_ql = ['NORTH PINES, YOSEMITE NATIONAL PARK']
# login
# print base_url
# b.visit(base_url)
#
# # search
# ele_list = b.find_by_id('locationCriteria')
# srch_box = ele_list.first
# srch_box.fill('Yosemite National Park,CA ')
#
# ele_list = b.find_by_text('Search')
# srch_btn = ele_list.first
# srch_btn.click()


arrive_date = 'Sat Jul 15 2017'
depart_date = 'Sat Jul 16 2017'

# park_description->campsite->entry link
target_parks = {
    'yosemite': {
        'north pines': 'https://www.recreation.gov/campsiteFilterAction.do?sitefilter=STANDARD%20NONELECTRIC&startIdx=0&contractCode=NRSO&parkId=70927',
        'upper pines': 'https://www.recreation.gov/campsiteFilterAction.do?sitefilter=STANDARD%20NONELECTRIC&startIdx=0&contractCode=NRSO&parkId=70925',
        'lower pines': 'https://www.recreation.gov/campsiteFilterAction.do?sitefilter=STANDARD%20NONELECTRIC&startIdx=0&contractCode=NRSO&parkId=70928'
    }
}

def error(s):
    print 'ERROR - %s' % s


def info(s):
    print 'INFO - %s' % s


def find_by_name(browser, name):
    ele_list = browser.find_by_name(name)
    return ele_list.first


def find_by_text(browser, text):
    ele_list = browser.find_by_text(text)
    return ele_list.first


def find_by_id(browser, id):
    ele_list = browser.find_by_id(id)
    return ele_list.first


def find_by_tag(element, tag):
    ele_list = element.find_by_tag(tag)
    return ele_list.first


def get_num_avail_sites_afer_search(b):
    # check # availables in search results
    match_summary = b.find_by_css('#contentArea > div > div.searchSummary > div.matchSummary')
    if match_summary.is_empty():
        error('can not find matchSummary in search results')
    # X site(s) available out of Y site(s)
    avail_str = match_summary.first.value
    info('search results summary : %s' % avail_str)
    if 'available out of' not in avail_str:
        error('availability summary does not match known pattern')
    try:
        num_avail_sites = int(avail_str.split()[0])
    except:
        error('fail to parse available site number')
    return num_avail_sites


def search_by_date(b, arrive_date, depart_date):
    txt = find_by_name(b, 'arrivalDate')
    txt.fill(arrive_date)
    txt = find_by_name(b, 'departureDate')
    txt.fill(depart_date)
    btn = find_by_text(b, 'Search')
    btn.click()


def get_table_rows(b):
    results = find_by_id(b, 'shoppingitems')
    table = find_by_tag(results, 'tbody')
    rows = table.find_by_tag('tr')
    return rows


def get_avails_from_search(b, arrive_date, depart_date):
    search_by_date(b, arrive_date, depart_date)
    num_avails = get_num_avail_sites_afer_search(b)
    return num_avails


def get_site_no2link(rows, num_avails_pg_1):
    no2link = {}
    for i in range(0, num_avails_pg_1):
        col0 = rows[i].find_by_tag('td').first
        site_a = col0.find_by_tag('a').last
        link = site_a['href']
        no = site_a.value
        no2link[no] = link
    return no2link

def try_book_first_avail(camp_entry_url):
    b = Browser(driver_name='chrome')
    b.visit(camp_entry_url)
    num_avails_pg_1 = get_avails_from_search(b, arrive_date, depart_date)
    if num_avails_pg_1 == 0:
        info('no available sites in XXX')
    info('number of available sites in first page: %s' % str(num_avails_pg_1))
    rows = get_table_rows(b)
    num_rows_pg_1 = len(rows)
    info('number of sites in first page: %s' % str(num_rows_pg_1))
    no2link = get_site_no2link()
    #TODO: try to book first available site and return

    for k in no2link:
        print k + '\t' + no2link[k]

    return True


# main
for p_name in target_parks:
    info('try to book park: %s' % p_name)
    campsites = target_parks[p_name]
    for c_name in campsites:
        info('try to book site: %s' % c_name)
        camp_entry_url = campsites[c_name]
        success = try_book_first_avail(camp_entry_url)
        if success:
            info('BOOKED!')
        else:
            info('FAILED: NO AVAILS/ERROR')
