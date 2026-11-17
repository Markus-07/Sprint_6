import allure

from data import BASE_URL
from pages.main_page import MainPage


@allure.epic("Навигация по логотипам")
class TestLogos:
    @allure.title("Логотип «Самоката» ведёт на главную страницу сервиса")
    def test_scooter_logo_opens_main_page(self, driver):
        main_page = MainPage(driver)
        main_page.open_main_page()
        main_page.click_scooter_logo()
        assert main_page.current_url().rstrip("/") == BASE_URL.rstrip("/")

    @allure.title("Логотип Яндекса открывает Дзен в новом окне")
    def test_yandex_logo_opens_dzen_in_new_window(self, driver):
        main_page = MainPage(driver)
        main_page.open_main_page()
        main_page.click_yandex_logo()
        assert "dzen.ru" in main_page.current_url()
