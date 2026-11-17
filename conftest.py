
import time

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions


@pytest.fixture(params=['firefox'])
def driver(request):
    options = FirefoxOptions()
    last_error = None
    for _ in range(3):
        try:
            driver = webdriver.Firefox(options=options)
            break
        except Exception as e:
            last_error = e
            time.sleep(2)
    else:
        raise last_error

    driver.maximize_window()
    yield driver
    driver.quit()
