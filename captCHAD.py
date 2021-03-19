from helium import *
from selenium.webdriver import ChromeOptions

import requests
import time
import os
import random

options = ChromeOptions()
options.add_argument('--incognito')


with open('updated_user_agents.txt', 'r') as user_agent_file:
    user_agent_list = [str(user_agent.strip('\n')) for user_agent in user_agent_file]


def pwn_recaptcha():
    options.add_argument('user-agent='+random.choice(user_agent_list))
    driver = start_chrome(url, options=options)
    og_window = str(driver.title)

    def activate_recaptcha():
        click(S(".recaptcha-checkbox-border"))
        wait_until(S("#recaptcha-audio-button").exists)
        click(S("#recaptcha-audio-button"))

    def solve_audio():
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
        scroll_down(1000)
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

        write(answer.lower(), into=S('#audio-response'))
        click(Button('Verify'))
        time.sleep(1)

        if Text('Multiple correct solutions required - please solve more.').exists():
            solve_audio()
        else:
            if Button('Submit').exists():
                click(Button('Submit'))

    wait_until(S('.g-recaptcha').exists)
#     print(S('.g-recaptcha').exists())

    wait_until(S('.recaptcha-checkbox-border').exists)
#     print(S('.recaptcha-checkbox-border').exists())

    activate_recaptcha()

    if Text("Try again later").exists():
        print("*** Change IP Address ***")
        driver.quit()
    else:
        solve_audio()


url = 'https://www.google.com/recaptcha/api2/demo'

pwn_recaptcha()
