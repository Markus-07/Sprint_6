import time
from datetime import date, timedelta

import allure
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage
from data import BASE_URL


class OrderPage(BasePage):

    # ---------- Первая форма ----------
    INPUT_NAME    = (By.XPATH, "//input[@placeholder='* Имя']")
    INPUT_SURNAME = (By.XPATH, "//input[@placeholder='* Фамилия']")
    INPUT_ADDRESS = (By.XPATH, "//input[@placeholder='* Адрес: куда привезти заказ']")
    INPUT_METRO   = (By.XPATH, "//input[@placeholder='* Станция метро']")
    INPUT_PHONE   = (By.XPATH, "//input[@placeholder='* Телефон: на него позвонит курьер']")
    BTN_NEXT      = (By.XPATH, "//div[contains(@class,'Order_NextButton')]//button[text()='Далее']")

    # ---------- Вторая форма ----------
    INPUT_DATE      = (By.XPATH, "//input[@placeholder='* Когда привезти самокат']")
    RENTAL_DROPDOWN = (By.XPATH, "//div[contains(@class,'Dropdown-control')]")
    RENTAL_OPTION   = "//div[contains(@class,'Dropdown-option') and text()='{period}']"
    COMMENT         = (By.XPATH, "//input[@placeholder='Комментарий для курьера']")
    BTN_BACK        = (By.XPATH, "//button[text()='Назад']")
    BTN_SUBMIT      = (By.XPATH, "//div[contains(@class,'Order_Buttons')]//button[text()='Заказать']")
    CHECKBOX_COLOR  = "//label[@for='{color}']"

    # ---------- Попап подтверждения ----------
    ORDER_MODAL  = (By.XPATH, "//div[contains(@class,'Order_Modal')]")
    BTN_YES      = (By.XPATH, "//button[normalize-space()='Да']")
    BTN_NO       = (By.XPATH, "//div[contains(@class,'Order_Modal')]//button[text()='Нет']")
    MODAL_HEADER = (By.XPATH, "//div[contains(@class,'Order_ModalHeader')]")
    TEXT_SUCCESS = (By.XPATH, "//*[contains(., 'Заказ оформлен')]")

    # ---------- Статус заказа ----------
    BTN_STATUS = (By.XPATH, "//div[contains(@class,'Order_NextButton')]//button[text()='Посмотреть статус']")

    # кнопка опции в списке станций: ul.select-search__options > li > button.select-search__option
    METRO_OPTION = (
        "//ul[contains(@class,'select-search__options')]//button"
        "[contains(@class,'select-search__option') and normalize-space()='{station}']"
    )

    def __init__(self, driver):
        super().__init__(driver, BASE_URL)

    @allure.step("Заполняем первую форму: имя, фамилия, адрес, метро, телефон")
    def fill_first_form(self, name, surname, address, phone, metro):
        self.type_text(self.INPUT_NAME, name)
        self.type_text(self.INPUT_SURNAME, surname)
        self.type_text(self.INPUT_ADDRESS, address)
        self._type_metro(metro)
        self.type_text(self.INPUT_PHONE, phone)

    @allure.step("Выбираем станцию метро «{metro}»")
    def _type_metro(self, metro):
        any_option = "//button[contains(@class,'select-search__option')]"

        for attempt in range(4):
            field = self.find(self.INPUT_METRO)
            self.click_element(field)
            field.send_keys(Keys.CONTROL, 'a')
            field.send_keys(Keys.DELETE)
            field.send_keys(metro)
            try:
                self.wait_condition(
                    lambda d: self.find_all_visible((By.XPATH, any_option)), timeout=5
                )
            except TimeoutException:
                continue  # список не открылся — пробуем заново

            # клавиатурный выбор: вниз + Enter
            field.send_keys(Keys.ARROW_DOWN)
            field.send_keys(Keys.ENTER)

            try:
                self.wait_condition(lambda d: field.get_attribute('value') == metro, timeout=5)
                return  # выбор засчитан и в поле, и в форме
            except TimeoutException:
                continue  # Enter не сработал — пробуем заново

        visible = [o.text for o in self.find_all_visible((By.XPATH, any_option))]
        raise AssertionError(
            f"Не удалось выбрать станцию '{metro}' за 4 попытки. "
            f"Последние видимые опции: {visible}"
        )

    @allure.step("Кликаем «Далее» и ждём вторую форму")
    def click_next(self):
        for attempt in range(3):
            btn = self.find(self.BTN_NEXT)
            self.scroll_to(btn)
            try:
                self.click_element(btn)
            except ElementClickInterceptedException:
                self.click_via_js(btn)
            try:
                self.wait_visible(self.INPUT_DATE, timeout=15)
                return  # вторая форма открылась
            except TimeoutException:
                continue

        self.attach_screenshot('form_state_on_failure')
        metro_val = self.get_attribute(self.INPUT_METRO, 'value')
        raise AssertionError(
            f'Вторая форма не открылась. Поле метро содержит: {metro_val!r}'
        )

    @allure.step("Заполняем вторую форму: дата, срок аренды «{period}», цвета, комментарий")
    def fill_second_form(self, period='сутки', colors=None, comment='', date=None):
        if colors is None:
            colors = ['black']
        self.type_text(self.INPUT_DATE, date or self._tomorrow())
        # сбрасываем фокус с поля даты, чтобы календарь не перекрывал дропдаун
        self.find(self.INPUT_DATE).send_keys(Keys.ENTER)
        self.click(self.RENTAL_DROPDOWN)
        self.click((By.XPATH, self.RENTAL_OPTION.format(period=period)))
        for color in colors:
            self.click((By.XPATH, self.CHECKBOX_COLOR.format(color=color)))
        if comment:
            self.type_text(self.COMMENT, comment)

    @allure.step("Кликаем «Заказать»")
    def click_submit(self):
        self.click(self.BTN_SUBMIT)

    @allure.step("Подтверждаем заказ кнопкой «Да»")
    def confirm_order(self):
        self.wait_visible(self.MODAL_HEADER)
        time.sleep(0.5)  # ждём, пока модалка дорисуется

        for attempt in range(3):
            buttons = self.find_all_visible(self.BTN_YES)
            assert buttons, 'Видимой кнопки «Да» в модалке нет'
            btn = buttons[0]
            try:
                self.click_element(btn)
            except ElementClickInterceptedException:
                self.click_via_js(btn)
            try:
                self.wait_condition(
                    lambda d: self.find_all_visible(self.TEXT_SUCCESS), timeout=3
                )
                return True
            except TimeoutException:
                continue

        self.attach_screenshot('confirm_failure')
        raise AssertionError('Кнопка «Да» не сработала: окно «Заказ оформлен» не появилось')

    @allure.step("Ждём окно «Заказ оформлен»")
    def assert_order_created(self):
        try:
            self.wait_condition(
                lambda d: self.find_all_visible(self.TEXT_SUCCESS), timeout=10
            )
            return True
        except TimeoutException:
            headers = [h.text for h in self.find_all(self.MODAL_HEADER)]
            yes = self.find_all(self.BTN_YES)
            raise AssertionError(
                f'Заголовков модалки на странице: {headers}. '
                f'Кнопок «Да»: {len(yes)}, видимых: {sum(b.is_displayed() for b in yes)}'
            )

    @allure.step("Открываем страницу статуса заказа")
    def view_status(self):
        self.click(self.BTN_STATUS)

    @staticmethod
    def _tomorrow():
        return (date.today() + timedelta(days=1)).strftime('%d.%m.%Y')
