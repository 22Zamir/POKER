import cv2
import numpy as np
from PIL import ImageGrab


class ScreenReader:
    def __init__(self):
        self.template_dir = "templates/"
        self.card_templates = {}
        self.button_templates = {}

    def load_templates(self):
        """Загружает шаблоны карт и кнопок."""
        # Шаблоны карт
        card_names = ["As", "Ad", "Ah", "Ac", "Ks", "Kh", "Kd", "Kc", ...]
        for name in card_names:
            path = f"{self.template_dir}{name}.png"
            try:
                template = cv2.imread(path, 0)
                self.card_templates[name] = template
            except:
                print(f"Не найден шаблон: {path}")

        # Кнопки
        self.button_templates = {
            "CHECK": cv2.imread(f"{self.template_dir}check.png", 0),
            "RAISE": cv2.imread(f"{self.template_dir}raise.png", 0),
            "FOLD": cv2.imread(f"{self.template_dir}fold.png", 0),
        }

    def detect_hand_cards(self, image):
        """Находит карты на руках."""
        cards = []
        for card_name, template in self.card_templates.items():
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            for pt in zip(*locations[::-1]):
                cards.append(card_name)
        return cards

    def detect_buttons(self, image):
        """Находит координаты кнопок."""
        buttons = {}
        for btn_name, template in self.button_templates.items():
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.8)
            for pt in zip(*locations[::-1]):
                buttons[btn_name] = pt
        return buttons
