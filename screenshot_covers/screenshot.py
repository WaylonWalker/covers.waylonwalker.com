import json
import os
import time
from pathlib import Path
from subprocess import Popen

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.remote.errorhandler import JavascriptException

# take screenshot

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver)
width = 1200
height = 600
driver.set_window_size(width, height)


import logging

logger = logging.getLogger()


def get_screenshot(slug):
    logger.info(f"getting {slug}")
    print(f"getting {slug}")

    driver.get(f"https://waylonwalker.com/{slug}")
    driver.execute_script("document.querySelector('html').style.overflow='hidden'")
    driver.execute_script("document.head.insertAdjacentHTML('beforeend', '<style>html {zoom: 118%;} #title-wrapper{aspect-ratio:1.55;} #title-wrapper h1 {word-break:break-word;}</style>')")
    try:
        driver.execute_script(
            "window.scrollTo(0, document.querySelector('article').getBoundingClientRect().y)"
        )
    except JavascriptException:
        try:
            driver.execute_script(
                "window.scrollTo(0, document.querySelector('nav').clientHeight)"
            )
        except JavascriptException:
            ...
    time.sleep(0.05)
    pic_file = driver.get_screenshot_as_png()
    driver.save_screenshot("pageImage.png")

    im = Image.open("pageImage.png")
    file = Path(f"pngs/{slug}.png")
    file.parent.mkdir(exist_ok=True)
    im.save(file)


def main():
    r = requests.get("https://waylonwalker.com/markata.json")
    for slug in [a.get("slug", "") for a in json.loads(r.content)["articles"]]:
        if not Path(f"pngs/{slug}.png").exists():
            get_screenshot(slug)

        if not Path(f"static/{slug}.jpg").exists():
            cmd = (
                """npx @squoosh/cli --mozjpeg '{"quality":75,"baseline":false,"arithmetic":false,"progressive":true,"optimize_coding":true,"smoothing":0,"color_space":3,"quant_table":3,"trellis_multipass":false,"trellis_opt_zero":false,"trellis_opt_table":false,"trellis_loops":1,"auto_subsample":true,"chroma_subsample":2,"separate_chroma_quality":false,"chroma_quality":75}' """
                + str(Path(f"pngs/{slug}.png"))
                + f" --output-dir static/{Path(slug).parent}"
            )
            proc = Popen(cmd, shell=True)
            proc.wait()


if __name__ == "__main__":
    main()
