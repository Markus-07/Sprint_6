from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CLICK_RETRY = (2, 3)


class BasePage:
    def __init__(self, driver, url=None):
        self.driver = driver
        self.url = url

    def go(self):
        if self.url:
            self.driver.get(self.url)

    def find(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def type_text(self, locator, text):
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)
        return el

    def click(self, locator, timeout=10):
        # клик с ретраем: если элемент перерисовался в момент клика — пробуем снова
        for _ in range(CLICK_RETRY[1]):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                ).click()
                return
            except StaleElementReferenceException:
                continue
    def find_all(self, locator):
        """Возвращает все найденные элементы по локатору."""
        return self.driver.find_elements(*locator)

    def scroll_to(self, element):
        self.driver.execute_script(
            'arguments[0].scrollIntoView({block: "center"});', element
        )
        
    def find_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
