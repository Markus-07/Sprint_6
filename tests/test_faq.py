import allure
import pytest

from data import FAQ_ANSWERS
from pages.faq_page import FaqPage
from pages.main_page import MainPage


@allure.epic("Вопросы о важном")
class TestFaqQuestions:
    """Проверяем: по клику на стрелочку открывается соответствующий текст."""

    @allure.title("Вопрос о важном №{index} раскрывает нужный текст")
    @pytest.mark.parametrize("index,expected_fragment", FAQ_ANSWERS)
    def test_faq_opens_expected_answer(self, driver, index, expected_fragment):
        main_page = MainPage(driver)
        faq_page = FaqPage(driver)
        main_page.open_main_page()
        faq_page.click_question(index)
        assert expected_fragment in faq_page.get_answer_text(index), (
            f"Ответ на вопрос №{index} не содержит текст: «{expected_fragment}»"
        )
