import sys
import os
import joblib
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QScrollArea, QFrame, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DepressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.depression_names = {
            0: "Тип 0: Клинологически значимая депрессия отсутствует (No clinically significant depression)",
            1: "Тип 1: Минимальная / Легкая депрессия (Minimal / Mild depression)",
            2: "Тип 2: Умеренная депрессия (Moderate depression)",
            3: "Тип 3: Умеренно-тяжелая депрессия (Moderately-severe depression)",
            4: "Тип 4: Тяжелая депрессия (Severe depression)",
            5: "Тип 5: Дистимия / Дистимическое расстройство (Persistent depressive disorder / Dysthymia)",
            6: "Тип 6: Сезонное аффективное расстройство (Seasonal affective pattern)",
            7: "Тип 7: Перинатальная / Послеродовая депрессия (Peripartum / Postpartum depression)",
            8: "Тип 8: Депрессивный эпизод в рамках биполярного расстройства (Bipolar-related depressive episode)",
            9: "Тип 9: Ситуативная / Реактивная депрессия (Situational / Reactive depression)",
            10: "Тип 10: Психотическая депрессия (Psychotic depression)",
            11: "Тип 11: Другое уточненное депрессивное расстройство (Other specified depressive disorder)"
        }
        self.initUI()
        self.loadModel()

    def loadModel(self):
        model_path = 'random_forest_model.pkl'
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.predict_btn.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке модели: {e}")
                self.predict_btn.setEnabled(False)
        else:
            QMessageBox.critical(self, "Ошибка", f"Файл {model_path} не найден!")
            self.predict_btn.setEnabled(False)

    def initUI(self):
        self.setWindowTitle('Система прогназирования ментального здоровья')
        self.resize(750, 800)

        main_layout = QVBoxLayout()

        title = QLabel("Анкета оценки психологического состояния пациента")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-top: 10px; margin-bottom: 5px; color: #1a237e;")
        main_layout.addWidget(title)

        description = QLabel(
            "Заполните все разделы анкеты. На основе анализа признаков модель определит тип депрессивного состояния.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #555; margin-bottom: 15px;")
        main_layout.addWidget(description)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.questions_layout = QVBoxLayout(scroll_content)

        self.categorical_questions = {
            'Gender': ("Пол пациента:", {"Мужской": 0, "Женский": 1}),
            'Age': ("Возрастная группа (кодированная):",
                    {"До 18 лет": 10, "От 18 до 25 лет": 25, "Больше 25 лет": 35}),
            'Education_Level': ("Уровень образования:", {
                "Начальное или ниже": 0,
                "Среднее / Высшая школа": 1,
                "Высшее (Бакалавриат)": 2,
                "Магистратура / Аспирантура и выше": 3
            }),
            'Employment_Status': ("Статус занятости:", {
                "Безработный": 0,
                "Студент": 1,
                "Трудоустроен": 2,
                "Самозанятый": 3,
                "Другое": 4
            }),
            'Symptoms': ("Основной симптоматический кластер:", {
                "Нарушение сна": 0,
                "Потеря аппетита": 1,
                "Апатия и тревога": 2,
                "Когнитивные нарушения": 3,
                "Хроническая усталость": 4,
                "Спад энергии / Усталость": 5,
                "Перепады настроения": 6,
                "Раздражительность": 7,
                "Соматические жалобы (боли, слабость)": 8,
                "Социальная изоляция": 9,
                "Мысли о безнадежности": 10,
                "Другие проявления": 11,
                "Повышенная тревожность": 12,
                "Проблемы с концентрацией внимания": 13,
                "Чувство вины или никчемности": 14
            }),
            'Low_Energy': ("Наблюдается ли низкий уровень энергии?", {"Нет": 0, "Да": 1, "Иногда / Изредка": 2}),
            'Low_SelfEsteem': ("Испытываете ли вы проблемы с самооценкой?", {"Нет": 0, "Да": 1, "Иногда": 2}),
            'Search_Depression_Online': ("Ищете ли вы информацию о депрессии в Сети?", {"Нет": 0, "Да": 1}),
            'Worsening_Depression': ("Замечаете ли вы ухудшение состояния со временем?", {"Нет": 0, "Да": 1}),

            'How many times you eat ': ("Частота приема пищи в день:", {
                "2 раза или меньше": 0,
                "3 раза и больше": 1
            }),
            'SocialMedia_WhileEating': ("Использование соцсетей / гаджетов во время еды:", {
                "Никогда": 0,
                "Редко": 1,
                "Часто": 2,
                "Всегда": 3
            }),
            'Coping_Methods': ("Основной метод справления со стрессом:", {
                "Общение с близкими / друзьями": 0,
                "Занятия спортом / Активность": 1,
                "Хобби / Творчество": 2,
                "Избегание / Изоляция": 3,
                "Профессиональная терапия": 4,
                "Просмотр медиаконтента / Игры": 5,
                "Медитация / Релаксация": 6,
                "Регулирование режима дня": 7,
                "Вредные привычки": 8,
                "Рефлексия / Ведение дневника": 9,
                "Трудоголизм / Учеба": 10,
                "Религиозные / Духовные практики": 11,
                "Здоровый сон / Отдых": 12,
                "Путешествия / Прогулки на природе": 13
            }),
            'Self_Harm': ("Были ли факты или мысли о причинении себе вреда?", {"Нет": 0, "Да": 1}),
            'Mental_Health_Support': ("Обращались ли вы когда-либо за профессиональной психологической помощью?",
                                      {"Нет": 0, "Да": 1}),
            'Suicide_Attempts': ("Количество суицидальных попыток в прошлом:", {
                "Ни одной (None)": 0,
                "Одна": 1,
                "Две": 2,
                "Три и более": 3
            })
        }

        self.inputs = {}

        for col, (text, options) in self.categorical_questions.items():
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet(
                "background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 5px;")
            frame_layout = QVBoxLayout(frame)

            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 10, QFont.Weight.Medium))
            frame_layout.addWidget(lbl)

            combo = QComboBox()
            for opt_text in options.keys():
                combo.addItem(opt_text)
            frame_layout.addWidget(combo)

            self.questions_layout.addWidget(frame)
            self.inputs[col] = ('combo', combo)

        self.numeric_questions = {
            'Your overeating level': ("Уровень склонности к перееданию (0 - нет, 1-4 легкая, 5-8 умеренная, 9-12 тяжелая):", 0, 12, 0),
            'Depression_Score': ("Балл по шкале депрессии (от 0 до 30):", 0, 30, 12),
            'Sleep_Hours': ("Среднее количество часов сна в сутки (от 4 до 10):", 4, 10, 7),
            'SocialMedia_Hours': ("Сколько часов в день уходит на социальные сети? (от 0 до 12):", 0, 12, 3),
            'Nervous_Level': ("Уровень общей нервозности / тревоги (от 0 до 10):", 0, 10, 4)
        }

        for col, (text, min_v, max_v, default_v) in self.numeric_questions.items():
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet(
                "background-color: #f1f3f9; border: 1px solid #d0d7de; border-radius: 4px; margin-bottom: 5px;")
            frame_layout = QVBoxLayout(frame)

            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 10, QFont.Weight.Medium))
            frame_layout.addWidget(lbl)

            spin = QSpinBox()
            spin.setRange(min_v, max_v)
            spin.setValue(default_v)
            frame_layout.addWidget(spin)

            self.questions_layout.addWidget(frame)
            self.inputs[col] = ('spin', spin)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.predict_btn = QPushButton("Запустить прогназирование")
        self.predict_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.predict_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a237e; 
                color: white; 
                padding: 12px; 
                border-radius: 6px;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #283593;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
            }
        """)
        self.predict_btn.clicked.connect(self.makePrediction)
        main_layout.addWidget(self.predict_btn)

        self.setLayout(main_layout)

    def makePrediction(self):
        features_dict = {}

        for col, (field_type, widget) in self.inputs.items():
            if field_type == 'combo':
                txt = widget.currentText()
                features_dict[col] = self.categorical_questions[col][1][txt]
            elif field_type == 'spin':
                features_dict[col] = widget.value()

        try:
            expected_features = list(self.model.feature_names_in_)

            final_features = {}
            for feat in expected_features:
                if feat in features_dict:
                    final_features[feat] = features_dict[feat]
                else:
                    final_features[feat] = 0

            input_df = pd.DataFrame([final_features])

            input_df = input_df[expected_features]
            prediction = int(self.model.predict(input_df)[0])

            result_type_name = self.depression_names.get(prediction, "Неизвестный тип состояния")
            result_text = f"<p style='font-size:12pt; color:#1a237e;'><b>{result_type_name}</b></p>"

            msg = QMessageBox(self)
            msg.setWindowTitle("Результат анализа")
            msg.setText(result_text)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить прогноз.\nДетали: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DepressionApp()
    ex.show()
    sys.exit(app.exec())