import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from data import BASE_URL
from selenium.common.exceptions import TimeoutException


class MainPage(BasePage):

    BTN_TOP_ORDER    = (By.XPATH, "//div[contains(@class,'Header_Header')]//button[text()='Заказать']")
    BTN_BOTTOM_ORDER = (By.XPATH, "//div[contains(@class,'Home_FinishButton')]//button")
    BTN_COOKIE = (By.XPATH, "//div[contains(@class,'App_CookieConsent')]//button")
    SCOOTER_LOGO = (By.XPATH, "//a[contains(@class,'Header_LogoScooter')]")
    YANDEX_LOGO  = (By.XPATH, "//a[contains(@class,'Header_LogoYandex')]")

    def __init__(self, driver):
        super().__init__(driver, BASE_URL)

    @allure.step("Открываем главную страницу Самоката")
    def open(self):
        self.go()
        self.wait_visible(self.BTN_TOP_ORDER)
        try:
            self.click(self.BTN_COOKIE, timeout=3)
        except Exception:
            pass  # баннер уже могли закрыть в прошлом запуске сессии

    @allure.step("Закрываем баннер про куки, если он появился")
    def close_cookies(self):
        try:
            self.click(self.BTN_COOKIE, timeout=3)
        except Exception:
            pass  # баннера нет — просто идём дальше

    @allure.step("Открываем главную страницу Самоката (синоним open)")
    def open_main_page(self):
        """Синоним open() — так метод называется в тестах FAQ и логотипов."""
        self.open()

    @allure.step("Кликаем по кнопке «Заказать» ({entry})")
    def click_order_button(self, entry):
        locator = self.BTN_TOP_ORDER if entry == 'top' else self.BTN_BOTTOM_ORDER
        self.click(locator)

    @allure.step("Кликаем по логотипу Самоката")
    def click_scooter_logo(self):
        self.click(self.SCOOTER_LOGO)

    @allure.step("Кликаем по логотипу Яндекса и дожидаемся открытия Дзена")
    def click_yandex_logo(self):
        old = self.window_handles()
        for attempt in range(3):
            self.click(self.YANDEX_LOGO)
            try:
                self.wait_new_window(old, timeout=5)
                self.switch_to_window()
                self.wait_url_contains('dzen.ru', timeout=10)
                return
            except TimeoutException:
                continue  # окно не открылось или Дзен не загрузился — пробуем снова
        raise AssertionError('Новое окно с Дзеном не открылось после клика по логотипу Яндекса')


