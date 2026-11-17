import allure
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CLICK_RETRY = (2, 3)


class BasePage:
    def __init__(self, driver, url=None):
        self.driver = driver
        self.url = url

    @allure.step('Открыть страницу')
    def go(self):
        if self.url:
            self.driver.get(self.url)

    @allure.step('Найти элемент')
    def find(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    @allure.step('Дождаться видимости элемента')
    def wait_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    @allure.step('Ввести текст')
    def type_text(self, locator, text):
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)
        return el

    @allure.step('Клик по элементу')
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

    @allure.step('Клик через JavaScript')
    def click_via_js(self, element):
        """Кликает по элементу через JavaScript."""
        self.driver.execute_script('arguments[0].click();', element)

    @allure.step('Клик по найденному элементу')
    def click_element(self, element):
        """Кликает по уже найденному элементу, с ретраем на перерисовку."""
        for _ in range(CLICK_RETRY[1]):
            try:
                element.click()
                return
            except StaleElementReferenceException:
                continue

    @allure.step('Найти все элементы по локатору')
    def find_all(self, locator):
        """Возвращает все найденные элементы по локатору."""
        return self.driver.find_elements(*locator)

    @allure.step('Найти все видимые элементы по локатору')
    def find_all_visible(self, locator):
        """Возвращает только видимые элементы по локатору."""
        return [el for el in self.find_all(locator) if el.is_displayed()]

    @allure.step('Получить атрибут элемента')
    def get_attribute(self, locator, attr):
        return self.find(locator).get_attribute(attr)

    @allure.step('Дождаться выполнения условия')
    def wait_condition(self, condition, timeout=10):
        return WebDriverWait(self.driver, timeout).until(condition)

    @allure.step('Получить текущий URL')
    def current_url(self):
        return self.driver.current_url

    @allure.step('Прокрутить к элементу')
    def scroll_to(self, element):
        self.driver.execute_script(
            'arguments[0].scrollIntoView({block: "center"});', element
        )

    @allure.step('Список открытых окон браузера')
    def window_handles(self):
        return self.driver.window_handles

    @allure.step('Переключаемся на последнее открытое окно')
    def switch_to_window(self, index=-1):
        self.driver.switch_to.window(self.driver.window_handles[index])

    @allure.step('Дожидаемся появления нового окна')
    def wait_new_window(self, old_handles, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.window_handles) > len(old_handles)
        )

    @allure.step('Дожидаемся, что в адресной строке появится «{fragment}»')
    def wait_url_contains(self, fragment, timeout=10):
        self.wait_condition(
            lambda d: fragment in d.current_url, timeout=timeout
        )


    @allure.step('Прикрепить скриншот к отчёту')
    def attach_screenshot(self, name='screenshot'):
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
