from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from data import BASE_URL


class MainPage(BasePage):

    BTN_TOP_ORDER    = (By.XPATH, "//div[contains(@class,'Header_Header')]//button[text()='Заказать']")
    BTN_BOTTOM_ORDER = (By.XPATH, "//div[contains(@class,'Home_FinishButton')]//button")
    BTN_COOKIE = (By.XPATH, "//div[contains(@class,'App_CookieConsent')]//button")
    SCOOTER_LOGO = (By.XPATH, "//a[contains(@class,'Header_LogoScooter')]")
    YANDEX_LOGO  = (By.XPATH, "//a[contains(@class,'Header_LogoYandex')]")

    def __init__(self, driver):
        super().__init__(driver, BASE_URL)

    def open(self):
        self.go()
        self.wait_visible(self.BTN_TOP_ORDER)
        try:
            self.click(self.BTN_COOKIE, timeout=3)
        except Exception:
            pass  # баннер уже могли закрыть в прошлом запуске сессии

    def open_main_page(self):
        """Синоним open() — так метод называется в тестах FAQ и логотипов."""
        self.open()

    def click_order_button(self, entry):
        locator = self.BTN_TOP_ORDER if entry == 'top' else self.BTN_BOTTOM_ORDER
        self.click(locator)

    def click_scooter_logo(self):
        self.click(self.SCOOTER_LOGO)

    def click_yandex_logo(self):
        self.click(self.YANDEX_LOGO)
        
    def scroll_to(self, element):
        self.driver.execute_script(
            'arguments[0].scrollIntoView({block: "center"});', element
        )
