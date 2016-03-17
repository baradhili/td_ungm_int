# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
from splinter import Browser
import os
import urllib
import time
from datetime import datetime
import scraperwiki

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


def get_browse_soup(browser):
    html = browser.html
    soup = BeautifulSoup(html, "lxml")
    return soup


def browse(url):                                                                                            # loads all tenders
    browser = Browser("phantomjs", service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    browser.visit(portal)
    browser.find_by_id('lnkClearAll').first.click()
    time.sleep(2)
    return browser


def get_scroll_soup(url):
    browser = browse(url)
    soup = get_browse_soup(browser)
    num_tenders = soup.find('label', id="noticeSearchTotal").text
    print 'Number of Tenders: ', num_tenders
    scrolls = (int(num_tenders)/15)+5
    for i in range(0, scrolls):
        print i
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    soup = get_browse_soup(browser)
    print 'found links: ',len(soup.find('div', id="tblNotices").findAll('a'))
    return soup


def get_links(url):
    soup = get_scroll_soup(url)
    links = soup.find('div', id="tblNotices").findAll('a')
    return links


def get_soup(url):
    html = urllib.urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    return soup


def get_info(soup, type, next):
    try:
        info = soup.find('label', {"for":type})\
            .findNext(next).text.strip()
    except:
        info = ''
    return info


def get_other_info(soup, base, text):
    try:
        country = soup.find(base, text=text)\
            .findNext('div').text.strip()
    except:
        country = ''
    return country


def get_file(soup):
    files = []
    try:
        file_soup = soup.find('table', id="tblLinks").findAll('tr')
        for f in file_soup:
            files.append(f.findNext('td').text.encode('utf-8'))
    except:
        files = []
    return files


def get_docs(soup, base_url):
    docs = []
    try:
        doc_links = soup.findAll('a', {"class":"lnkShowDocument"})
        for d in doc_links:
            docs.append(base_url + d['href'])
    except:
        docs = []
    return docs


def get_unspsc_types(soup):
    types = []
    try:
        type_soup = soup.find('div', {"class":"unspscNode"}).findAll('span')
        for t in type_soup:
            types.append(t.text.strip().encode('utf-8'))
    except:
        types = []
    return types




if __name__ == '__main__':


    todays_date = str(datetime.now())
    portal = 'https://www.ungm.org/Public/Notice'
    base_url = 'https://www.ungm.org'
    links = get_links(portal)
    errors = []
    try:

        for link in links:

            try:
                tender_url = base_url + link['href']
                print tender_url
                tender_soup = get_soup(tender_url)
                tender_id = tender_url[-5:]
                notice_type = get_info(tender_soup, "NoticeType", 'span')
                registration_level= get_info(tender_soup, "RegistrationLevel", 'span')
                title = get_info(tender_soup, "Title", 'span')
                un_organisation = get_info(tender_soup, "AgencyId", 'span')
                reference = get_info(tender_soup, "Reference", 'span')
                date_published = get_info(tender_soup, "DatePublished", 'span')
                deadline = get_info(tender_soup, "Deadline", 'span')
                timezone = get_info(tender_soup, "Timezone", 'span')
                description = get_info(tender_soup, "Description", 'div')
                country = get_other_info(tender_soup, 'legend', 'Countries')
                email = get_info(tender_soup, "Email", 'span')
                first_name = get_info(tender_soup, "FirstName", 'span')
                last_name = get_info(tender_soup, "LastName", 'span')
                phone_country_code = get_info(tender_soup, "TelephoneCountryId", 'span')
                phone_number = get_info(tender_soup, "TelephoneNumber", 'span')
                phone_extension = get_info(tender_soup, "TelephoneExtension", 'span')
                fax_country_code = get_info(tender_soup, "FaxCountryId", 'span')
                fax = get_info(tender_soup, "Fax number", 'span')
                contact_text = get_info(tender_soup, "ContactText", 'span')
                files = get_file(tender_soup)
                docs = get_docs(tender_soup, base_url)
                unspsc_types = get_unspsc_types(tender_soup)
            except Exception as e:
                errors.append([link, e.message])
                continue


            data = {"tender_url":unicode(tender_url),
                    "tender_id": unicode(tender_id),
                    "notice_type": unicode(notice_type),
                    "registration_level": unicode(registration_level),
                    "title": unicode(title),
                    "un_organisation": unicode(un_organisation),
                    "reference": unicode(reference),
                    "date_published": unicode(date_published),
                    "deadline": unicode(deadline),
                    "timezone": unicode(timezone),
                    "description": unicode(description),
                    "country": unicode(country),
                    "email": unicode(email),
                    "first_name": unicode(first_name),
                    "last_name": unicode(last_name),
                    "phone_country_code": unicode(phone_country_code),
                    "phone_number": unicode(phone_number),
                    "phone_extension": unicode(phone_extension),
                    "fax_country_code": unicode(fax_country_code),
                    "fax": unicode(fax),
                    "contact_text": unicode(contact_text),
                    "files": unicode('files'),
                    "docs": unicode(docs),
                    "unspsc_types": unicode(unspsc_types),
                    "date": todays_date}

            scraperwiki.sqlite.save(unique_keys=['tender_url'], data=data)

        print 'No. errors ', len(errors)
        print errors

    except KeyboardInterrupt:
        print "forced kill"
        os._exit(0)


