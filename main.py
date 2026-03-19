import os
import random
import requests
from io import BytesIO
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex

from data import *

# Настройка окна для теста на ПК
Window.size = (400, 700)


# Вспомогательная функция для создания красивых кнопок
def create_button(text, on_press, color='#2196F3'):
    btn = Button(
        text=text,
        size_hint_y=None,
        height=60,
        background_normal='',
        background_color=get_color_from_hex(color),
        color=(1, 1, 1, 1),
        font_size='16sp'
    )
    btn.bind(on_press=on_press)
    # Скругление углов
    btn.canvas.before.add(Color(*get_color_from_hex(color)))
    btn.canvas.before.add(RoundedRectangle(pos=btn.pos, size=btn.size, radius=[10]))
    return btn


class MainScreen(Screen):
    """Главный экран с динамической навигацией по меню"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.menu_stack = []  # для навигации назад
        self.current_menu = main_menu
        self.current_title = "ЕГЭ Математика"
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical')

        # Верхняя панель
        top_bar = BoxLayout(size_hint_y=0.1, padding=[10, 5])
        with top_bar.canvas.before:
            Color(0.2, 0.6, 0.2, 1)  # зеленый фон
            self.bar_rect = RoundedRectangle(pos=top_bar.pos, size=top_bar.size, radius=[0])
        top_bar.bind(pos=self.update_bar_rect, size=self.update_bar_rect)

        self.back_btn = Button(
            text='←',
            size_hint_x=0.15,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size='24sp'
        )
        self.back_btn.bind(on_press=self.go_back)
        self.back_btn.opacity = 0
        self.back_btn.disabled = True

        self.title_label = Label(
            text=self.current_title,
            size_hint_x=0.7,
            color=(1, 1, 1, 1),
            font_size='20sp',
            bold=True
        )

        top_bar.add_widget(self.back_btn)
        top_bar.add_widget(self.title_label)
        layout.add_widget(top_bar)

        # Область прокрутки для кнопок меню
        scroll = ScrollView()
        self.menu_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[20, 10])
        self.menu_layout.bind(minimum_height=self.menu_layout.setter('height'))
        scroll.add_widget(self.menu_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.show_menu(main_menu, "ЕГЭ Математика")

    def update_bar_rect(self, instance, value):
        self.bar_rect.pos = instance.pos
        self.bar_rect.size = instance.size

    def show_menu(self, menu_items, title, stack=True):
        """Отображает список кнопок меню"""
        self.current_title = title
        self.title_label.text = title
        self.menu_layout.clear_widgets()

        for item in menu_items:
            btn = create_button(item, self.on_menu_item, self.get_color_for_item(item))
            self.menu_layout.add_widget(btn)

        # Обновление кнопки назад
        if stack and menu_items != main_menu:
            self.menu_stack.append(menu_items)
            self.back_btn.opacity = 1
            self.back_btn.disabled = False
        elif menu_items == main_menu:
            self.menu_stack.clear()
            self.back_btn.opacity = 0
            self.back_btn.disabled = True

    def get_color_for_item(self, item):
        """Возвращает цвет кнопки в зависимости от раздела"""
        if item.startswith('🧮'):
            return '#4CAF50'  # зеленый
        elif item.startswith('📐'):
            return '#2196F3'  # синий
        elif item.startswith('🧊'):
            return '#00BCD4'  # голубой
        elif item.startswith('📐') and 'Тригонометрия' in item:
            return '#FF9800'  # оранжевый
        elif item.startswith('🎲'):
            return '#9C27B0'  # фиолетовый
        elif item.startswith('📈'):
            return '#F44336'  # красный
        elif item.startswith('📊'):
            return '#3F51B5'  # индиго
        elif item.startswith('📋'):
            return '#795548'  # коричневый
        elif item.startswith('📝'):
            return '#E91E63'  # розовый
        elif item.startswith('💬'):
            return '#607D8B'  # серо-синий
        elif 'Вернуться' in item:
            return '#9E9E9E'  # серый
        else:
            return '#2196F3'

    def on_menu_item(self, instance):
        text = instance.text

        # Обработка верхнего уровня
        if self.current_menu == main_menu:
            if text == "🧮 Алгебра":
                self.current_menu = algebra_menu
                self.show_menu(algebra_menu, "Алгебра")
            elif text == "📐 Планиметрия":
                self.current_menu = planimetry_menu
                self.show_menu(planimetry_menu, "Планиметрия")
            elif text == "🧊 Стереометрия":
                self.current_menu = stereometry_menu
                self.show_menu(stereometry_menu, "Стереометрия")
            elif text == "📐 Тригонометрия":
                self.current_menu = trigonometry_menu
                self.show_menu(trigonometry_menu, "Тригонометрия")
            elif text == "🎲 Вероятность":
                self.current_menu = probability_menu
                self.show_menu(probability_menu, "Вероятность")
            elif text == "📈 Производные":
                self.current_menu = derivatives_menu
                self.show_menu(derivatives_menu, "Производные")
            elif text == "📊 Графики":
                self.current_menu = graphs_menu
                self.show_menu(graphs_menu, "Графики")
            elif text == "📋 Задания ЕГЭ":
                self.current_menu = ege_tasks_menu
                self.show_menu(ege_tasks_menu, "Задания ЕГЭ")
            elif text == "📝 Тест (1-12)":
                self.manager.get_screen('test').start_test()
                self.manager.current = 'test'
            elif text == "💬 Обратная связь":
                self.current_menu = feedback_menu
                self.show_menu(feedback_menu, "Обратная связь")

        # Алгебра и подменю
        elif self.current_menu == algebra_menu:
            if text == "Прогрессия":
                self.current_menu = progressiya_menu
                self.show_menu(progressiya_menu, "Прогрессия")
            elif text == "Квадратные уравнения":
                self.current_menu = kvadr_ur_menu
                self.show_menu(kvadr_ur_menu, "Квадратные уравнения")
            elif text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        elif self.current_menu == progressiya_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = algebra_menu
                self.show_menu(algebra_menu, "Алгебра")

        elif self.current_menu == kvadr_ur_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = algebra_menu
                self.show_menu(algebra_menu, "Алгебра")

        # Планиметрия и подменю
        elif self.current_menu == planimetry_menu:
            if text == "Треугольник":
                self.current_menu = treugolnik_menu
                self.show_menu(treugolnik_menu, "Треугольник")
            elif text == "Прямоугольный треугольник":
                self.current_menu = rect_treug_menu
                self.show_menu(rect_treug_menu, "Прямоугольный треугольник")
            elif text == "Равносторонний треугольник":
                self.current_menu = ravnostor_treug_menu
                self.show_menu(ravnostor_treug_menu, "Равносторонний треугольник")
            elif text == "Равносторонний шестиугольник":
                self.current_menu = shestiugolnik_menu
                self.show_menu(shestiugolnik_menu, "Шестиугольник")
            elif text == "Трапеция":
                self.current_menu = trapeciya_menu
                self.show_menu(trapeciya_menu, "Трапеция")
            elif text == "Ромб":
                self.current_menu = romb_menu
                self.show_menu(romb_menu, "Ромб")
            elif text == "Окружность":
                self.current_menu = okruzhnost_menu
                self.show_menu(okruzhnost_menu, "Окружность")
            elif text == "Произвольный четырёхугольник":
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        elif self.current_menu in [treugolnik_menu, rect_treug_menu, ravnostor_treug_menu,
                                   shestiugolnik_menu, trapeciya_menu, romb_menu, okruzhnost_menu]:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = planimetry_menu
                self.show_menu(planimetry_menu, "Планиметрия")

        # Стереометрия
        elif self.current_menu == stereometry_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        # Тригонометрия
        elif self.current_menu == trigonometry_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        # Вероятность
        elif self.current_menu == probability_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        # Производные
        elif self.current_menu == derivatives_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        # Графики
        elif self.current_menu == graphs_menu:
            if text in formulas:
                self.show_formula(text)
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

        # Задания ЕГЭ
        elif self.current_menu == ege_tasks_menu:
            if text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")
            else:
                self.show_popup("Описание заданий временно недоступно")

        # Обратная связь
        elif self.current_menu == feedback_menu:
            if text == "Писать сюда":
                self.show_popup("Функция обратной связи будет добавлена позже")
            elif text == "Вернуться в главное меню":
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика")

    def show_formula(self, name):
        """Показывает экран с формулой"""
        screen = self.manager.get_screen('formula')
        screen.show_formula(name, formulas.get(name, ''))
        self.manager.current = 'formula'

    def go_back(self, instance):
        """Возврат к предыдущему меню"""
        if self.menu_stack:
            self.menu_stack.pop()
            if self.menu_stack:
                prev_menu = self.menu_stack[-1]
            else:
                prev_menu = main_menu
                self.back_btn.opacity = 0
                self.back_btn.disabled = True

            if prev_menu == main_menu:
                self.current_menu = main_menu
                self.show_menu(main_menu, "ЕГЭ Математика", stack=False)
            elif prev_menu == algebra_menu:
                self.current_menu = algebra_menu
                self.show_menu(algebra_menu, "Алгебра", stack=False)
            elif prev_menu == planimetry_menu:
                self.current_menu = planimetry_menu
                self.show_menu(planimetry_menu, "Планиметрия", stack=False)
            # ... можно добавить остальные, но общий механизм уже работает

    def show_popup(self, message):
        popup = Popup(title='Информация',
                      content=Label(text=message, text_size=(280, None), halign='center'),
                      size_hint=(0.8, 0.4))
        popup.open()


class FormulaScreen(Screen):
    """Экран отображения формулы с картинкой"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'formula'
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical')

        # Кнопка назад
        back_btn = Button(
            text='← Назад',
            size_hint_y=0.1,
            background_normal='',
            background_color=get_color_from_hex('#f44336'),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        # ScrollView для контента
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        content.bind(minimum_height=content.setter('height'))

        self.title_label = Label(
            text='',
            size_hint_y=None,
            height=50,
            font_size='20sp',
            bold=True,
            color=(0, 0, 0, 1)
        )
        content.add_widget(self.title_label)

        self.image = Image(
            size_hint_y=None,
            height=300,
            allow_stretch=True,
            keep_ratio=True
        )
        content.add_widget(self.image)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def show_formula(self, title, url):
        self.title_label.text = title
        self.image.source = ''
        self.image.reload()
        if url:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    self.image.texture = CoreImage(img_data, ext='jpg').texture
                    self.image.height = 300
                else:
                    self.image.texture = None
                    self.title_label.text = title + "\n(Ошибка загрузки изображения)"
            except:
                self.image.texture = None
                self.title_label.text = title + "\n(Нет интернета или ошибка загрузки)"

    def go_back(self, instance):
        self.manager.current = 'main'


class TestScreen(Screen):
    """Экран тестирования"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'test'
        self.reset_state()
        self.build_ui()

    def reset_state(self):
        self.current_question = 0
        self.correct_answers = 0
        self.answers = []
        self.wrong_questions = []
        self.in_test = False
        self.retry_mode = False
        self.test_data = []

    def build_ui(self):
        layout = BoxLayout(orientation='vertical')

        # Верхняя панель
        top_bar = BoxLayout(size_hint_y=0.1, padding=[10, 5])
        with top_bar.canvas.before:
            Color(0.2, 0.6, 0.2, 1)
            self.bar_rect = RoundedRectangle(pos=top_bar.pos, size=top_bar.size, radius=[0])
        top_bar.bind(pos=self.update_bar_rect, size=self.update_bar_rect)

        self.back_btn = Button(
            text='← Меню',
            size_hint_x=0.2,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        self.back_btn.bind(on_press=self.confirm_exit)

        self.progress_label = Label(
            text='Тест',
            size_hint_x=0.8,
            color=(1, 1, 1, 1),
            font_size='16sp',
            halign='right'
        )
        self.progress_label.bind(size=self.progress_label.setter('text_size'))

        top_bar.add_widget(self.back_btn)
        top_bar.add_widget(self.progress_label)
        layout.add_widget(top_bar)

        # Область вопроса
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=15)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.question_label = Label(
            text='',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(0, 0, 0, 1),
            font_size='16sp'
        )
        self.question_label.bind(size=self.question_label.setter('text_size'))
        self.content.add_widget(self.question_label)

        self.question_image = Image(
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=True
        )
        self.content.add_widget(self.question_image)

        self.answer_input = TextInput(
            hint_text='Введите ответ',
            size_hint_y=None,
            height=50,
            multiline=False,
            font_size='16sp',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.content.add_widget(self.answer_input)

        self.submit_btn = create_button('Ответить', self.submit_answer, '#2196F3')
        self.content.add_widget(self.submit_btn)

        self.skip_btn = create_button('Пропустить', self.skip_question, '#FF9800')
        self.content.add_widget(self.skip_btn)

        scroll.add_widget(self.content)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def update_bar_rect(self, instance, value):
        self.bar_rect.pos = instance.pos
        self.bar_rect.size = instance.size

    def start_test(self):
        self.reset_state()
        self.in_test = True
        self.test_data = test_data
        self.show_question()

    def retry_wrong(self):
        if not self.wrong_questions:
            return
        self.current_question = 0
        self.correct_answers = 0
        self.answers = []
        self.in_test = True
        self.retry_mode = True
        self.test_data = [test_data[i] for i in self.wrong_questions]
        self.wrong_questions = []
        self.show_question()

    def show_question(self):
        if self.current_question < len(self.test_data):
            q = self.test_data[self.current_question]
            self.progress_label.text = f"{self.current_question + 1}/{len(self.test_data)}"
            self.question_label.text = q['question']

            if q.get('photo'):
                try:
                    response = requests.get(q['photo'], timeout=5)
                    if response.status_code == 200:
                        img_data = BytesIO(response.content)
                        self.question_image.texture = CoreImage(img_data, ext='jpg').texture
                        self.question_image.height = 200
                    else:
                        self.question_image.height = 0
                except:
                    self.question_image.height = 0
            else:
                self.question_image.height = 0

            self.answer_input.text = ''
        else:
            self.finish_test()

    def submit_answer(self, instance):
        if not self.in_test:
            return
        answer = self.answer_input.text.strip()
        q = self.test_data[self.current_question]
        correct = answer.lower() == q['correct_answer'].lower()

        self.answers.append({
            'question': q['question'],
            'user_answer': answer,
            'correct': correct,
            'correct_answer': q['correct_answer'],
            'solution': q['solution']
        })

        if correct:
            self.correct_answers += 1
            self.show_popup("Правильно!", "green")
        else:
            self.wrong_questions.append(self.current_question)
            self.show_popup(f"Неверно!\nПравильный ответ: {q['correct_answer']}\n\n{q['solution']}", "red")

        self.current_question += 1
        Clock.schedule_once(lambda dt: self.show_question(), 1.5)

    def skip_question(self, instance):
        if not self.in_test:
            return
        q = self.test_data[self.current_question]
        self.answers.append({
            'question': q['question'],
            'user_answer': 'пропущено',
            'correct': False,
            'correct_answer': q['correct_answer'],
            'solution': q['solution']
        })
        self.current_question += 1
        self.show_popup(f"Правильный ответ: {q['correct_answer']}\n\n{q['solution']}", "orange")
        Clock.schedule_once(lambda dt: self.show_question(), 1.5)

    def finish_test(self):
        self.in_test = False
        total = len(self.test_data)
        correct = self.correct_answers

        if correct == total:
            result = "ИДЕАЛЬНО! Все ответы верны!"
        elif correct >= total * 0.8:
            result = f"Отличный результат! {correct}/{total}"
        elif correct >= total * 0.6:
            result = f"Хорошо! {correct}/{total}"
        elif correct >= total * 0.4:
            result = f"Неплохо! {correct}/{total}"
        else:
            result = f"{correct}/{total}. Нужно подтянуть теорию!"

        # Показываем результат
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=result, halign='center', size_hint_y=None, height=100))

        if self.wrong_questions:
            retry_btn = create_button('Повторить ошибки', lambda x: self.retry_test(), '#FF9800')
            content.add_widget(retry_btn)

        ok_btn = create_button('В меню', lambda x: self.back_to_menu(), '#4CAF50')
        content.add_widget(ok_btn)

        popup = Popup(title='Результат', content=content, size_hint=(0.8, 0.6))
        popup.open()

    def retry_test(self):
        self.retry_wrong()
        self.manager.current = 'test'

    def back_to_menu(self):
        self.manager.current = 'main'

    def confirm_exit(self, instance):
        if self.in_test:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text='Вы уверены, что хотите прервать тест?'))
            btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            yes_btn = create_button('Да', lambda x: self.exit_test(), '#f44336')
            no_btn = create_button('Нет', lambda x: self.dismiss_popup(), '#4CAF50')
            btn_layout.add_widget(yes_btn)
            btn_layout.add_widget(no_btn)
            content.add_widget(btn_layout)
            self.popup = Popup(title='Подтверждение', content=content, size_hint=(0.8, 0.4))
            self.popup.open()
        else:
            self.manager.current = 'main'

    def exit_test(self):
        self.popup.dismiss()
        self.in_test = False
        self.manager.current = 'main'

    def dismiss_popup(self):
        self.popup.dismiss()

    def show_popup(self, message, color='blue'):
        popup = Popup(title='Результат',
                      content=Label(text=message, halign='center', text_size=(300, None)),
                      size_hint=(0.8, 0.4))
        popup.open()


class MathApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen())
        sm.add_widget(FormulaScreen())
        sm.add_widget(TestScreen())
        return sm


if __name__ == '__main__':
    MathApp().run()