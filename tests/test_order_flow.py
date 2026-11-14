from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import allure
import pytest

from pages.main_page import MainPage
from pages.order_page import OrderPage

from data import BASE_URL, ORDER_SCENARIOS

@pytest.mark.parametrize('entry, user', ORDER_SCENARIOS)
def test_full_order_flow(driver, entry, user):
    """Полный флоу: главная → две формы → подтверждение → окно успеха."""
    main = MainPage(driver)
    order = OrderPage(driver)

    main.open()
    main.close_cookies()

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
