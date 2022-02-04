from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

import modules.files as files

path_to_chrome = files.get_path('chrome_driver')
browser = webdriver.Chrome(path_to_chrome)
browser.implicitly_wait(5)

sku = 16598369
browser.get(f'https://www.wildberries.ru/catalog/{sku}/detail.aspx')

size_label = browser.find_element(By.XPATH, "//li[@class='sizes-list__item'][2]/label[@class='j-size']")
size_label.click()

to_basket_button = browser.find_element(By.CLASS_NAME, 'btn-main')
to_basket_button.click()

browser.get('https://www.wildberries.ru/lk/basket')

plus_button = browser.find_element(By.XPATH, "//button[@class='count__plus plus']")
browser.implicitly_wait(1)
i = 0
while(True):
    plus_button.click()
    i += 1
    if i == 30:
        try:
            plus_button = browser.find_element(By.XPATH, "//button[@class='count__plus plus']")
            i = 0
        except:
            plus_button = browser.find_element(By.XPATH, "//button[@class='count__plus plus disabled']")
            print(f'Товар {sku} кончился')
            basket_count = browser.find_element(By.XPATH, "//h1[@class='basket-section__header active']")
            print(basket_count.get_dom_attribute("data-count"))
            break
browser.close()

