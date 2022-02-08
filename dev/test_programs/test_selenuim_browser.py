from selenium import webdriver
from selenium.webdriver.common.by import By

import modules.files as files

path_to_driver = files.get_path('chrome_driver')
browser = webdriver.Chrome(path_to_driver)
browser.implicitly_wait(5) # задержка загрузки элемента прежде чем выдать ошибку

sku = 16598369
browser.get(f'https://www.wildberries.ru/catalog/{sku}/detail.aspx')

# XPATH - это особым образом написанный путь, позволяющий найти элемент в разметке
# начало с // - значит относительный путь
size_label = browser.find_element(By.XPATH, "//li[@class='sizes-list__item'][2]/label[@class='j-size']")
size_label.click()

to_basket_button = browser.find_element(By.CLASS_NAME, 'btn-main')
to_basket_button.click()

browser.get('https://www.wildberries.ru/lk/basket')

plus_button = browser.find_element(By.XPATH, "//button[@class='count__plus plus']")
browser.implicitly_wait(1) # снижаем задержку перед ошибкой
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

