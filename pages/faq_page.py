import allure
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class FaqPage(BasePage):

    @allure.step("Формируем локатор вопроса №{index}")
    def question(self, index):
        return (By.ID, f"accordion__heading-{index}")


    @allure.step("Прокручиваем к вопросу №{index} и кликаем по нему")
    def click_question(self, index):
        q = self.find(self.question(index))
        self.scroll_to(q)
        try:
            q.click()
        except ElementClickInterceptedException:
            # картинка самоката перекрывает кнопку — кликаем через JS
            self.click_via_js(q)

    @allure.step("Читаем текст ответа на вопрос №{index}")
    def get_answer_text(self, index):
        return self.wait_visible((By.ID, f"accordion__panel-{index}")).text

