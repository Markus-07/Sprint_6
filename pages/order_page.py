import time
from datetime import date, timedelta

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

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
    BTN_YES      = (By.XPATH, "//div[contains(@class,'Order_Modal')]//button[text()='Да']")
    BTN_NO       = (By.XPATH, "//div[contains(@class,'Order_Modal')]//button[text()='Нет']")
    MODAL_HEADER = (By.XPATH, "//div[contains(@class,'Order_ModalHeader')]")

    # кнопка опции в списке станций: ul.select-search__options > li > button.select-search__option
    METRO_OPTION = (
        "//ul[contains(@class,'select-search__options')]//button"
        "[contains(@class,'select-search__option') and normalize-space()='{station}']"
    )

    def __init__(self, driver):
        super().__init__(driver, BASE_URL)

    def fill_first_form(self, name, surname, address, phone, metro):
        self.type_text(self.INPUT_NAME, name)
        self.type_text(self.INPUT_SURNAME, surname)
        self.type_text(self.INPUT_ADDRESS, address)
        self._type_metro(metro)
        self.type_text(self.INPUT_PHONE, phone)

    def _type_metro(self, metro):
        option_xp = self.METRO_OPTION.format(station=metro)
        any_option_xp = "//button[contains(@class,'select-search__option')]"

        def visible(d, xp):
            return [e for e in d.find_elements(By.XPATH, xp) if e.is_displayed()]

        for attempt in range(4):
            field = self.driver.find_element(*self.INPUT_METRO)
            field.click()
            field.send_keys(Keys.CONTROL, 'a')
            field.send_keys(Keys.DELETE)
            field.send_keys(metro)
            try:
                WebDriverWait(self.driver, 5).until(lambda d: visible(d, any_option_xp))
            except TimeoutException:
                continue  # список не открылся — пробуем заново

            # клавиатурный выбор: вниз + Enter
            field.send_keys(Keys.ARROW_DOWN)
            field.send_keys(Keys.ENTER)

            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: field.get_attribute('value') == metro
                )
                return  # выбор засчитан и в поле, и в форме
            except TimeoutException:
                continue  # Enter не сработал — пробуем заново

        raise AssertionError(
            f"Не удалось выбрать станцию '{metro}' за 4 попытки. "
            f"Последние видимые опции: "
            f"{[o.text for o in visible(self.driver, any_option_xp)]}"
        )


    def click_next(self):
        for attempt in range(3):
            btn = self.driver.find_element(*self.BTN_NEXT)
            self.scroll_to(btn)
            try:
                btn.click()
            except ElementClickInterceptedException:
                self.driver.execute_script('arguments[0].click();', btn)
            try:
                self.wait_visible(self.INPUT_DATE, timeout=15)
                return  # вторая форма открылась
            except TimeoutException:
                # на последней попытке вылетаем с понятной ошибкой
                if attempt == 2:
                    raise
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name='form_state_on_failure',
            attachment_type=allure.attachment_type.PNG,
        )
        metro_val = self.driver.find_element(*self.INPUT_METRO).get_attribute('value')
        raise AssertionError(
            f'Вторая форма не открылась. Поле метро содержит: {metro_val!r}'
        )


    def fill_second_form(self, period='сутки', colors=None, comment='', date=None):
        if colors is None:
            colors = ['black']
        self.type_text(self.INPUT_DATE, date or self._tomorrow())
        # сбрасываем фокус с поля даты, чтобы календарь не перекрывал дропдаун
        self.driver.find_element(*self.INPUT_DATE).send_keys(Keys.ENTER)
        self.click(self.RENTAL_DROPDOWN)
        self.click((By.XPATH, self.RENTAL_OPTION.format(period=period)))
        for color in colors:
            self.click((By.XPATH, self.CHECKBOX_COLOR.format(color=color)))
        if comment:
            self.type_text(self.COMMENT, comment)

    def click_submit(self):
        self.click(self.BTN_SUBMIT)

    def confirm_order(self):
        self.wait_visible(self.MODAL_HEADER)
        time.sleep(0.5)

        def all_yes(d):
            return [b for b in d.find_elements(By.XPATH, "//button[normalize-space()='Да']")
                    if b.is_displayed()]

        def success(d):
            return d.find_elements(By.XPATH, "//*[contains(., 'Заказ оформлен')]")

        btns = all_yes(self.driver)
        assert btns, 'Видимой кнопки «Да» в модалке нет'
        b = btns[0]

        # 1. Есть ли у кнопки onClick в React-пропсах
        react_info = self.driver.execute_script(
            "const el = arguments[0]; const out = [];"
            "for (const k of Object.keys(el)) {"
            "  if (k.startsWith('__reactProps')) {"
            "    out.push(Object.keys(el[k]).join(','));"
            "  }"
            "}"
            "return out.join(' | ') || 'react props не найдены';",
            b,
        )

        # 2. Клик как человек
        try:
            ActionChains(self.driver).move_to_element(b).click().perform()
            try:
                WebDriverWait(self.driver, 3).until(success)
                return True
            except TimeoutException:
                pass
        except Exception:
            pass

        # 3. Доверенный клик через CDP — на координаты кнопки
        try:
            r = b.rect
            x = int(r['x'] + r['width'] / 2)
            y = int(r['y'] + r['height'] / 2)
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent',
                {'type': 'mouseMoved', 'x': x, 'y': y})
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent',
                {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent',
                {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            try:
                WebDriverWait(self.driver, 3).until(success)
                return True
            except TimeoutException:
                pass
        except Exception as e:
            react_info += f'; CDP недоступен: {type(e).__name__}'

        # 4. Окно для ручного клика: нажми «Да» мышкой в браузере
        print('\n>>> У тебя 20 секунд: нажми «Да» руками в браузере Selenium!')
        time.sleep(20)
        try:
            WebDriverWait(self.driver, 2).until(success)
            print('>>> Ручной клик сработал — заказ оформлен!')
            return True
        except TimeoutException:
            pass

        api = self.get_order_api_status()
        try:
            modal_text = self.driver.find_element(
                By.XPATH, "//div[contains(@class,'Order_Modal')]"
            ).text
        except Exception:
            modal_text = 'модалка не найдена'
        raise AssertionError(
            f'Кнопка «Да» не сработает никак. React-пропсы кнопки: {react_info}. '
            f'Модалка: {modal_text!r}. Ответы API: {api}'
        )


    def get_order_api_status(self):
        """Собирает из performance-лога запросы и ответы к /orders."""
        import json
        events = []
        try:
            for entry in self.driver.get_log('performance'):
                try:
                    msg = json.loads(entry['message'])['message']
                except Exception:
                    continue
                if msg.get('method') == 'Network.requestWillBeSent':
                    req = msg['params']['request']
                    if 'orders' in req['url']:
                        events.append(f"{req['method']} {req['url']}")
                elif msg.get('method') == 'Network.responseReceived':
                    resp = msg['params']['response']
                    if 'orders' in resp['url']:
                        events.append(f"ответ {resp['status']} {resp['url']}")
        except Exception as e:
            return [f'логи недоступны: {type(e).__name__}: {e}']
        return events or ['ни одного запроса к /orders — обработчик не сработал']


    def assert_order_created(self):
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.XPATH, "//*[contains(., 'Заказ оформлен')]")
            )
            return True
        except TimeoutException:
            headers = [h.text for h in self.driver.find_elements(
                By.XPATH, "//div[contains(@class,'Order_ModalHeader')]"
            )]
            yes = self.driver.find_elements(By.XPATH, "//button[normalize-space()='Да']")
            raise AssertionError(
                f'Заголовков модалки на странице: {headers}. '
                f'Кнопок «Да»: {len(yes)}, видимых: {sum(b.is_displayed() for b in yes)}'
            )

    def view_status(self):
        self.click((By.XPATH, "//div[contains(@class,'Order_NextButton')]//button[text()='Посмотреть статус']"))

    @staticmethod
    def _tomorrow():
        return (date.today() + timedelta(days=1)).strftime('%d.%m.%Y')
