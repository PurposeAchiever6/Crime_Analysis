from seleniumbase import SB
from time import sleep
import csv

Gmail_name = "Your_Gmail_address"
Gmail_password = "Your_Gmail_password"

remove_list = ["https://policies.google.co",
               "https://support.google.co",
               "https://www.google.co",
               "https://maps.google.co",
               "https://accounts.google.co",
               "https://translate.google.co",
               "https://myactivity.google.co",
               "https://www.bing",
               "http://help.bing",
               "https://bing.co",
               "http://go.microsoft.co",
               "https://support.microsoft.co",
               "http://help.bing.microsoft.co",
               "https://go.microsoft.co",
               "https://www.microsoft.co"]

with open('Subject.txt', 'r') as file:
    subject_contents = file.read()
    subject_rows = subject_contents.split("\n")
with open('Object.txt', 'r') as file:
    object_contents = file.read()
    object_rows = object_contents.split("\n")

## 1. 10 pages from Google.co.uk
def google_co_uk(subject, object, sb):
    sb.open(f'https://www.google.co.uk/search?q={subject + " " + object}')
    # sleep(5)
    try:
        sb.click('div.r, a[class="gb_ta gb_dd gb_Ed gb_de"]', by="css selector")
    except Exception as e:
        print("no exist sighin button")
    # sleep(5)
    
    page_count = 1
    urls = []
    
    while page_count <= 10:
        search_results = sb.find_elements('div.r, a', by="css selector")
        for result in search_results:
           url = result.get_attribute('href')
           urls.append(url)
        try:
            sb.click("a[id='pnnext']", by="css selector")
        except Exception as e:
            break
        page_count += 1

    # print(urls)
    for url in urls:
       if url is not None and url.startswith("http") and not any(url.startswith(item) for item in remove_list):
        # print(url)
        all_urls[url] = [subject, object, "https://www.google.co.uk"]

## 2. 10 pages from Google.us
def google_us(subject, object, sb):
    sb.open(f'https://www.google.com/search?q={subject + " " + object}')
    # sleep(5)
    try:
        sb.click('div.r, a[class="gb_ta gb_dd gb_Ed gb_de"]', by="css selector")
    except Exception as e:
        print("no exist sighin button")
    # sleep(5)
    
    page_count = 1
    urls = []
    
    while page_count <= 10:
        search_results = sb.find_elements('div.r, a', by="css selector")
        for result in search_results:
           url = result.get_attribute('href')
           urls.append(url)
        try:
            sb.click("a[id='pnnext']", by="css selector")
        except Exception as e:
            break
        page_count += 1

    # print(urls)
    for url in urls:
       if url is not None and url.startswith("http") and not any(url.startswith(item) for item in remove_list):
        # print(url)
        all_urls[url] = [subject, object, "https://www.google.us"]

## 3. 5 pages from Bing.co.uk
def bing_co_uk(subject, object, sb):
    sb.open(f'https://www.bing.co.uk/search?q={subject + " " + object}')
    # sleep(5)
    # try:
    #     sb.click('a[id="id_l"]', by="css selector")
    # except Exception as e:
    #     print("no exist sighin button")
    # sleep(5)
    
    page_count = 1
    urls = []
    
    while page_count <= 5:
        search_results = sb.find_elements('div.r, a', by="css selector")
        for result in search_results:
           url = result.get_attribute('href')
           urls.append(url)
        try:
            sb.click("a[class='sb_pagN sb_pagN_bp b_widePag sb_bp ' ]", by="css selector")
        except Exception as e:
            break
        page_count += 1

    # print(urls)
    for url in urls:
       if url is not None and url.startswith("http") and not any(url.startswith(item) for item in remove_list):
        # print(url)
        all_urls[url] = [subject, object, "https://www.bing.co.uk"]

## 4. 5 pages from Bing.us
def bing_us(subject, object, sb):
    return(1)

all_urls = {}
# urls -> [subject, object, search_engine]

with SB(uc=True) as sb:
    sb.open("https://accounts.google.com/")
    sb.type("//input[@name='identifier']", Gmail_name)
    sb.click("//div[@id='identifierNext']")
    sb.type('input[type="password"]', Gmail_password)
    sb.click('button:contains("Next")')
    # sleep(5)
    for subject_row in subject_rows:
        for object_row in object_rows:
            google_co_uk(subject_row, object_row, sb)
            google_us(subject_row, object_row, sb)
            bing_co_uk(subject_row, object_row, sb)

file_path = 'url.csv'
all_urls_list = []
for key, value in all_urls.items():
    all_urls_list.append([key, value[0], value[1], value[2]])
with open(file_path, 'w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)
    # Write the data to the CSV file
    writer.writerows(all_urls_list)
