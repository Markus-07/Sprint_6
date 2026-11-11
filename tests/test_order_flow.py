from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import allure
import pytest

from pages.main_page import MainPage
from pages.order_page import OrderPage

BASE_URL = 'https://qa-scooter.praktikum-services.ru/'

# первый элемент — точка входа (кнопка «Заказать» сверху или снизу),
# второй — данные пользователя
ORDER_SCENARIOS = [
    ('top', {
        'name': 'Иван',
        'surname': 'Петров',
        'address': 'ул. Тверская, 1',
        'metro': 'Сокол',
        'phone': '+79991112233',
        'period': 'сутки',
        'colors': ['black'],
        'comment': 'Позвоните за полчаса',
        'date': None,  # None — возьмём завтрашний день
    }),
    ('bottom', {
        'name': 'Мария',
        'surname': 'Иванова',
        'address': 'ул. Арбат, 5',
        'metro': 'Комсомольская',
        'phone': '+79112223344',
        'period': 'двое суток',
        'colors': ['grey'],
        'comment': '',
        'date': None,
    }),
]


def close_cookies(driver):
    try:
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'да все привыкли')]"
        ).click()
    except NoSuchElementException:
        pass  # баннера нет — просто идём дальше


@pytest.mark.parametrize('entry, user', ORDER_SCENARIOS)
def test_full_order_flow(driver, entry, user):
    """Полный флоу: главная → две формы → подтверждение → окно успеха."""
    main = MainPage(driver)
    order = OrderPage(driver)

    main.open()
    close_cookies(driver)

    with allure.step('Клик по кнопке «Заказать»'):
        main.click_order_button(entry)

    with allure.step('Заполнение первой формы'):
        order.fill_first_form(
            name=user['name'],
            surname=user['surname'],
            address=user['address'],
            phone=user['phone'],
            metro=user['metro'],
        )

    with allure.step('Переход ко второй форме'):
        order.click_next()

    with allure.step('Заполнение второй формы'):
        order.fill_second_form(
            period=user['period'],
            colors=user['colors'],
            comment=user['comment'],
            date=user['date'],
        )

    with allure.step('Оформление заказа'):
        order.click_submit()
        order.confirm_order()

    with allure.step('Проверка окна «Заказ оформлен»'):
        assert order.assert_order_created(), \
            f'Окно «Заказ оформлен» не появилось (точка входа: {entry})'
