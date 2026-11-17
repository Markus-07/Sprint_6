import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from data import BASE_URL


class TrackPage(BasePage):

    INPUT_ORDER_NUMBER = (By.XPATH, "//input[contains(@class,'Track_Input')]")
    BTN_VIEW           = (By.XPATH, "//div[contains(@class,'Track_Form')]//button[text()='Посмотреть']")
    RESULT_BLOCK       = (By.XPATH, "//div[contains(@class,'Track_OrderColumns')]")
    ORDER_INFO         = (By.XPATH, "//div[contains(@class,'Track_OrderInfo')]")
    BTN_CANCEL_ORDER   = (By.XPATH, "//div[contains(@class,'Track_OrderInfo')]//button[text()='Отменить заказ']")

    TXT_NOT_FOUND = (By.XPATH, "//*[contains(@alt,'Такого заказа нет')]")

    def __init__(self, driver):
        super().__init__(driver, BASE_URL + 'track')

    @allure.step("Вводим номер заказа «{number}»")
    def enter_order_number(self, number):
        self.type_text(self.INPUT_ORDER_NUMBER, str(number))

    @allure.step("Кликаем «Посмотреть»")
    def click_view(self):
        self.click(self.BTN_VIEW)

    @allure.step("Проверяем, что заказ не найден")
    def assert_order_not_found(self):
        self.find(self.TXT_NOT_FOUND)
        return True

    @allure.step("Проверяем, что информация о заказе видна")
    def assert_order_info_visible(self):
        self.wait_visible(self.ORDER_INFO)
        return True
