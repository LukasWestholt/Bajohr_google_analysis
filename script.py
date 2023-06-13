# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, ElementNotSelectableException,\
    WebDriverException
from urllib.error import HTTPError
import socket
import re
import locale
import csv
import pyautogui

LOCALE = 'de_DE.UTF-8'


def get_ready_site():
    options = FirefoxOptions()
    # options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver


def normalize_data(i, is_integer=False):
    i = re.sub(r'[^\d.,]', '', i)
    locale.setlocale(locale.LC_ALL, LOCALE)
    if is_integer:
        return locale.atoi(i)
    else:
        return locale.atof(i)


def get_google_data(url, b):
    b.get(url)
    delay = 15  # seconds
    try:
        WebDriverWait(b, delay).until(ec.presence_of_element_located((By.ID, "result-stats")))
    except TimeoutException:
        try:
            b.find_element(By.ID, "captcha-form")
        except WebDriverException:
            print("no google stats found. Press enter for retry")
            input()
            return get_google_data(url, b)

        reaction = pyautogui.confirm('You have to solve the captcha. When it\'s solved, click Ok.',
                                     title="Confirm that the captcha is solved", buttons=['OK', 'I don\'t want to'])
        if reaction == "OK":
            return get_google_data(url, b)
        raise KeyboardInterrupt("Pressed exit button")

    data = b.find_element(By.ID, "result-stats").get_attribute('innerText')
    print(data)
    results_time = b.find_element(By.ID, "result-stats").find_element(By.TAG_NAME, "nobr").text
    results_count = data.replace(results_time.strip(), '').strip()
    return normalize_data(results_count, is_integer=True), normalize_data(results_time)


browser = get_ready_site()

# agree the terms and conditions
# browser.get("https://www.google.com/")
# WebDriverWait(browser, 10).until(
#    ec.element_to_be_clickable((By.ID, 'W0wltc'))
# ).click()

words = [word for word in open('input.txt', 'r', encoding="utf-8")]
set_words = [(word.strip(), words.count(word)) for word in set(words)]
num_lines = len(set_words)
count = 0
results = []
for word, occurrences in set_words:
    count += 1
    try:
        result = (word, occurrences, *get_google_data("https://www.google.com/search?q=%22" + word + "%22", browser))
        print(str(count) + "/" + str(num_lines) + ": " + str(result))
        results.append(result)
    except (TimeoutException, socket.timeout, HTTPError, ElementNotVisibleException,
            ElementNotSelectableException, WebDriverException, locale.Error, ValueError) as error:
        print(str(count) + "/" + str(num_lines) + ": " + word + " -> Error: " + str(error))

print(str(count) + " words checked")

with open('output.csv', 'w', newline='', encoding="utf-8") as out:
    csv_out = csv.writer(out)
    csv_out.writerow(['word', 'occurrences', 'google_count', 'google_seconds'])
    csv_out.writerows(results)

browser.quit()
