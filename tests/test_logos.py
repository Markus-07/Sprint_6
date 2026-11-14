import allure
from data import BASE_URL
from pages.main_page import MainPage
from selenium.webdriver.support.ui import WebDriverWait


@allure.epic("Навигация по логотипам")
class TestLogos:
    @allure.title("Логотип «Самоката» ведёт на главную страницу сервиса")
    def test_scooter_logo_opens_main_page(self, driver):
        main_page = MainPage(driver)
        main_page.open_main_page()
        main_page.click_scooter_logo()
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")

    @allure.title("Логотип Яндекса открывает Дзен в новом окне")
    def test_yandex_logo_opens_dzen_in_new_window(self, driver):
        main_page = MainPage(driver)
        main_page.open_main_page()
        main_page.click_yandex_logo()
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, 10).until(lambda d: 'dzen.ru' in d.current_url)
        assert 'dzen.ru' in driver.current_url
