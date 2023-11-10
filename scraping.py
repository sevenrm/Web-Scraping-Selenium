from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
import pandas as pd

options = Options()

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(
    options=options
)

url = 'https://www.sigmaaldrich.com/ES/en/products/analytical-chemistry/reference-materials/pharma-secondary-standards?country=ES&language=en&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=reference-materials&cmsRoute=pharma-secondary-standards&page=1&facets=facet_web_special_grade%3Apharmaceutical+secondary+standard'

driver.get(url)

product_datas = {
    'Product No.': [],
    'Description': [],
    'CAS': [],
    'Package Size': [],
    'Price(Euro)': [],
    'BP Traceability': [],
    'Ph.Eur Traceability': [],
    'USP Traceability': []
    
}

def get_product_data(product_url):
    product_data = {
        'no': '-',
        'description': '-',
        'CAS': '-',
        'pack_size': '-',
        'price': '-',
        'BP_trace': '-',
        'PH_EUR_trace': '-',
        'US_trace': '-'
    }
    trace_text = set()
    access_url = "https://www.sigmaaldrich.com" + product_url
    # access_url = "https://www.sigmaaldrich.com/BE/en/product/sial/phr1084"
    driver.get(access_url)
    sop = BeautifulSoup(driver.page_source, 'html.parser')
    # print(sop.find(id="product-number"))
    element = sop.find_all(class_=lambda x: x and "MuiTypography-body2" in x)
    element_table = sop.find_all(class_=lambda x: x and "MuiTableCell-body" in x)
    # print(element_table)
    span_elements = element[4].find_all('span')
    for span in span_elements:
        trace_text.add(span.text)
    # print(span_elements)
    print(trace_text)
    product_data['no'] = sop.find(id="product-number").get_text()
    product_data['description'] = sop.find(id="product-name").get_text()
    product_data['CAS'] = sop.find(id=lambda x: x and "-alias-link" in x).get_text()
    product_data['pack_size'] = element_table[1].get_text().replace(" ", "").upper()
    product_data['price'] = "EUR " + element_table[3].get_text().replace("€", "")
    for text in trace_text:
        if (not text.find("traceable to BP")):
            if product_data['BP_trace'] != '-':
                product_data['BP_trace'] = product_data['BP_trace'] + "/" + text.replace("traceable to BP", "").replace(" ", "")
            else:
                product_data['BP_trace'] = text.replace("traceable to BP", "").replace(" ", "")
        elif (not text.find("traceable to Ph. Eur.")):
            if product_data['PH_EUR_trace'] != '-':
                product_data['PH_EUR_trace'] = product_data['PH_EUR_trace'] + "/" + text.replace("traceable to Ph. Eur.", "").replace(" ", "")
            else:
                product_data['PH_EUR_trace'] = text.replace("traceable to Ph. Eur.", "").replace(" ", "")
        elif (not text.find("traceable to USP")):
            if product_data['US_trace'] != '-':
                product_data['US_trace'] = product_data['US_trace'] + "/" + text.replace("traceable to USP", "").replace(" ", "")
            else:
                product_data['US_trace'] = text.replace("traceable to USP", "").replace(" ", "")
    save_data(product_data)
    print(product_data)

def save_data(data):
    product_datas['Product No.'].append(data['no'])
    product_datas['Description'].append(data['description'])
    product_datas['CAS'].append(data['CAS'])
    product_datas['Package Size'].append(data['pack_size'])
    product_datas['Price(Euro)'].append(data['price'])
    product_datas['BP Traceability'].append(data['BP_trace'])
    product_datas['Ph.Eur Traceability'].append(data['PH_EUR_trace'])
    product_datas['USP Traceability'].append(data['US_trace'])

soup = BeautifulSoup(driver.page_source, 'html.parser')
result = soup.find(class_="jss122")
page = 0
result_array = []
while page < 3:
    page += 1
    result_a = result.find_all('a')
    result_array.append(result_a)
    # print(result_array)
    next_page = driver.find_element(By.CSS_SELECTOR, '[aria-label="Go to next page"]')
    print(next_page)
    driver.execute_script("arguments[0].scrollIntoView();", next_page)
    next_page.click()
    # print(next_page)

    # print(result_href)

# for product_url in result_href:
#     get_product_data(product_url)

    
# print(product_datas)
# df = pd.DataFrame(product_datas)
# sorted_df = df.sort_values('Product No.')
# sorted_df.to_excel('result.xlsx', index=False)

driver.quit()
