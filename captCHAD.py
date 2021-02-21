from helium import *
from selenium.webdriver import ChromeOptions

import requests
import time
import os
import random

options = ChromeOptions()
options.add_argument('--incognito')
options.add_argument('window-size=1200,800')

url = 'https://www.google.com/recaptcha/api2/demo'


def pwn_recaptcha(url):
    driver = start_chrome(url, headless=False, options=options)

    og_window = str(driver.title)

    click(S(".recaptcha-checkbox-border"))
    wait_until(S("#recaptcha-audio-button").exists)
    click(S("#recaptcha-audio-button"))
    wait_until(S("#audio-instructions").exists)
    click(Button("Play"))

    src = driver.find_element_by_id("audio-source").get_attribute("src")
    print(src)

    r = requests.get(src)

    with open("recaptcha_audio.mp3", 'wb') as f:
        f.write(r.content)

    # ASK WATSON

    watson_url = 'https://speech-to-text-demo.ng.bluemix.net/'
    driver.execute_script(f"window.open('{watson_url}');")

    switch_to('Speech to Text Demo')
    scroll_down(2000)
    wait_until(S('.tab-panels').exists)
    time.sleep(random.uniform(1, 2))

    audio_file_path = os.path.join(os.getcwd(), "recaptcha_audio.mp3")
    drag_file(audio_file_path, to=Button('Upload Audio File'))
    wait_until(S('//*[@id="root"]/div/div[7]/div/div/div/span').exists)
    answer_element = driver.find_element_by_xpath('//*[@id="root"]/div/div[7]/div/div/div/span')
    answer = answer_element.get_attribute('innerHTML')
    print(answer)

    driver.close()

    switch_to(og_window)

    write(answer, into=S('#audio-response'))
    click(Button('Verify'))
    wait_until(S('.recaptcha-checkbox-checkmark').exists)
    time.sleep(1)
    click(Button('Submit'))


pwn_recaptcha(url)


