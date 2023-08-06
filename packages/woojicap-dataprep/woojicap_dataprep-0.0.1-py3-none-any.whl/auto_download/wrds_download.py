import os
import random
import shutil
from datetime import datetime
from time import sleep

from selenium import webdriver


def download_all(browser, username, password, default_download_path, target_download_path):
    base_delay = 1
    random_delay = 1  # set random breaks between each operation, to prevent being blocked
    driver = init_driver(browser=browser)

    init_login(driver=driver, username=username, password=password)

    url = 'https://wrds-web.wharton.upenn.edu/wrds/ds/compd/index/constituents.cfm?navId=83'
    driver.get(url)
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_id('search_option_method3')
    box.click()
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_id('select_all_button-80DBA1CF')
    box.click()
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_id('csv')
    box.click()
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_id('form_submit')
    box.click()
    __delay_between_requests(base_time=10 * base_delay, delta_time=random_delay)

    driver.switch_to.window(driver.window_handles[1])
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    while True:
        main = driver.find_element_by_id('main')
        ps = main.find_elements_by_tag_name('p')
        if 'Your output is complete' in ps[0].text:
            break
        __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    file_name = ps[1].text.split(' ')[0]
    box = driver.find_element_by_link_text(file_name)
    box.click()
    __delay_between_requests(base_time=10 * base_delay, delta_time=random_delay)

    dst_file_name = 'index_constituents_{}.csv'.format(datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    dst_file_path = os.path.join(target_download_path, dst_file_name)
    shutil.copytree(os.path.join(default_download_path, file_name), dst_file_path)
    print('Successfully download data to: {}'.format(dst_file_path))

    return True


def __delay_between_requests(base_time, delta_time):
    sleep(base_time + delta_time * random.random())


def init_driver(browser):
    if browser == 'Chrome':
        driver = webdriver.Chrome()
    elif browser == 'Firefox':
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Edge()
    return driver


def init_login(driver, username, password, base_delay=1, random_delay=1):
    driver.get('https://wrds-www.wharton.upenn.edu/login')
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_name('username')
    box.send_keys(username)
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_name('password')
    box.send_keys(password)
    __delay_between_requests(base_time=base_delay, delta_time=random_delay)

    box = driver.find_element_by_name('submit')
    box.click()
    __delay_between_requests(base_time=10 * base_delay, delta_time=random_delay)
