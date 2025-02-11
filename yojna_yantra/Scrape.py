import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import requests

def make_request(url):
    response = requests.get(url)
    time.sleep(5)  
    return response

def extract_scheme_details(driver, link, name):
    scheme_details = {'name': name, 'url': link}
    response = make_request(link)
    
    if response.status_code == 200:
        driver.get(link)
        time.sleep(2)
        
        try:
            scheme_details['details'] = driver.find_element(By.CSS_SELECTOR, '#details').text
            scheme_details['benefits'] = driver.find_element(By.CSS_SELECTOR, '#benefits').text
            scheme_details['eligibility'] = driver.find_element(By.CSS_SELECTOR, '#eligibility').text
            scheme_details['application_process'] = driver.find_element(By.CSS_SELECTOR, '#application-process').text
            scheme_details['documents_required'] = driver.find_element(By.CSS_SELECTOR, '#documents-required').text
        except Exception as e:
            print(f"Error extracting details for {link}: {e}")
    
    return scheme_details

def get_links(driver):
    link_list = []
    while True:
        result_page_container = driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center')
        result_page = result_page_container.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center > div.mt-2')
        time.sleep(1)
        
        links = result_page.find_elements(By.TAG_NAME, 'a')
        for link in links:
            link_list.append((link.get_attribute('href'), link.text))
        
        time.sleep(2)
        try:
            pagination_container = driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center > div.mt-2 > div.mt-4')
            next_button = pagination_container.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center > div.mt-2 > div.mt-4 > ul > svg.ml-2.text-darkblue-900.dark\:text-white.cursor-pointer')
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Reached the last page or encountered an error: {e}")
            break
    return link_list

if __name__ == '__main__':
    driver = webdriver.Edge()
    driver.get("https://www.myscheme.gov.in/search/state/Maharashtra")
    time.sleep(2)

    all_schemes_button_container = driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center > div.mt-4')
    all_schemes_button = all_schemes_button_container.find_element(By.CSS_SELECTOR, '#__next > div > main > div > div.grid.grid-cols-4.gap-4.container.mx-auto.px-4.relative > div.sm\:col-span-3.col-span-4.items-center.justify-center > div.mt-4 > div.overflow-x-auto.overflow-y-hidden.flex.flex-row.items-center.mb-2.border-0.border-b.border-solid.border-gray-200.pr-2.md\:pr-4.no-scrollbar.border-none > div:nth-child(3) > span')
    all_schemes_button.click()
    time.sleep(2)

    link_list = get_links(driver)

    all_scheme_details = []
    for link, name in link_list:
        details = extract_scheme_details(driver, link, name)
        all_scheme_details.append(details)

    with open('scheme_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_scheme_details, f, ensure_ascii=False, indent=4)

    driver.quit()