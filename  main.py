
import requests
import webbrowser
import io
import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.025, 0.025, 0.04, 1)

PURPLE = (0.55, 0.2, 1, 1)
DARK = (0.09, 0.07, 0.14, 1)
WHITE = (1, 1, 1, 1)

class RobloxFinder(App):

    def build(self):
        self.user_id = None
        self.place_id = None
        self.game_id = None
        self.history_file = "roblox_history.json"
        self.history = self.load_history()

        scroll = ScrollView(do_scroll_x=False)

        root = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=13,
            size_hint_y=None
        )
        root.bind(minimum_height=root.setter("height"))

        title = Label(
            text="[b]ROBLOX PLAYER FINDER[/b]",
            markup=True,
            font_size=26,
            color=PURPLE,
            size_hint_y=None,
            height=65
        )
        root.add_widget(title)

        self.entry = TextInput(
            hint_text="Введи нік або ID гравця",
            multiline=False,
            size_hint_y=None,
            height=55,
            background_color=DARK,
            foreground_color=WHITE,
            cursor_color=PURPLE
        )
        root.add_widget(self.entry)

        search = self.make_button("🔎  ЗНАЙТИ ГРАВЦЯ")
        search.bind(on_press=self.search)
        root.add_widget(search)

        self.avatar = Image(
            size_hint_y=None,
            height=260,
            allow_stretch=True,
            keep_ratio=True
        )
        root.add_widget(self.avatar)

        self.info = self.make_label(
            "Профіль гравця з'явиться тут",
            21,
            85
        )
        root.add_widget(self.info)

        self.status = self.make_label(
            "СТАТУС: НЕ ВІДОМО",
            18,
            45
        )
        self.status.color = PURPLE
        root.add_widget(self.status)

        self.stats = self.make_label(
            "Друзі: —     Підписники: —\nПідписки: —",
            16,
            65
        )
        root.add_widget(self.stats)

        self.about = self.make_label(
            "Опис профілю: —",
            15,
            100
        )
        root.add_widget(self.about)

        self.copy_button = self.make_button("📋  СКОПІЮВАТИ ID")
        self.copy_button.disabled = True
        self.copy_button.bind(on_press=self.copy_id)
        root.add_widget(self.copy_button)

        self.profile = self.make_button("🌐  ВІДКРИТИ ПРОФІЛЬ")
        self.profile.disabled = True
        self.profile.bind(on_press=self.open_profile)
        root.add_widget(self.profile)

        self.join = self.make_button("🎮  ПРИЄДНАТИСЯ ДО ГРИ")
        self.join.disabled = True
        self.join.bind(on_press=self.join_game)
        root.add_widget(self.join)

        history_title = self.make_label(
            "ОСТАННІ ПОШУКИ",
            20,
            45
        )
        history_title.color = PURPLE
        root.add_widget(history_title)

        self.history_box = GridLayout(
            cols=1,
            spacing=7,
            size_hint_y=None
        )
        self.history_box.bind(
            minimum_height=self.history_box.setter("height")
        )
        root.add_widget(self.history_box)

        self.update_history()

        scroll.add_widget(root)
        return scroll

    def make_label(self, text, font_size, height):
        return Label(
            text=text,
            font_size=font_size,
            color=WHITE,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=height
        )

    def make_button(self, text):
        return Button(
            text=text,
            size_hint_y=None,
            height=53,
            background_normal="",
            background_color=(0.32, 0.08, 0.62, 1),
            color=WHITE,
            font_size=15,
            bold=True
        )

    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False)
        except Exception:
            pass

    def add_history(self, name):
        self.history = [
            item for item in self.history
            if item.lower() != name.lower()
        ]
        self.history.insert(0, name)
        self.history = self.history[:5]
        self.save_history()
        self.update_history()

    def update_history(self):
        if not hasattr(self, "history_box"):
            return

        self.history_box.clear_widgets()

        if not self.history:
            self.history_box.add_widget(
                self.make_label("Пошуків поки немає", 14, 40)
            )
            return

        for name in self.history:
            button = self.make_button("↻  " + name)
            button.bind(
                on_press=lambda instance, n=name: self.search_history(n)
            )
            self.history_box.add_widget(button)

    def search_history(self, name):
        self.entry.text = name
        self.search(None)

    def search(self, instance):
        name = self.entry.text.strip()

        if not name:
            self.info.text = "Введи нік або ID!"
            return

        self.user_id = None
        self.place_id = None
        self.game_id = None

        self.profile.disabled = True
        self.join.disabled = True
        self.copy_button.disabled = True

        self.avatar.texture = None
        self.info.text = "Шукаю гравця..."
        self.status.text = "СТАТУС: ПЕРЕВІРКА..."
        self.stats.text = "Завантажую статистику..."
        self.about.text = "Завантажую опис профілю..."

        try:
            if name.isdigit():
                response = requests.get(
                    f"https://users.roblox.com/v1/users/{name}",
                    timeout=15
                )
                response.raise_for_status()
                user = response.json()
            else:
                response = requests.post(
                    "https://users.roblox.com/v1/usernames/users",
                    json={
                        "usernames": [name],
                        "excludeBannedUsers": False
                    },
                    timeout=15
                )
                response.raise_for_status()
                users = response.json().get("data", [])

                if not users:
                    self.info.text = "Гравця не знайдено!"
                    self.status.text = "СТАТУС: —"
                    self.stats.text = "—"
                    self.about.text = "—"
                    return

                user = users[0]

                response = requests.get(
                    f"https://users.roblox.com/v1/users/{user['id']}",
                    timeout=15
                )
                response.raise_for_status()
                user = response.json()

            self.user_id = user["id"]

            self.info.text = (
                f"Нік: {user.get('name', '—')}\n"
                f"Ім'я: {user.get('displayName', '—')}\n"
                f"ID: {self.user_id}"
            )

            self.about.text = (
                "Опис профілю:\n"
                + (user.get("description") or "Опис відсутній")
            )

            self.profile.disabled = False
            self.copy_button.disabled = False

            self.add_history(user.get("name", name))
            self.load_avatar()
            self.check_presence()
            self.load_stats()

        except Exception:
            self.info.text = (
                "Помилка пошуку!\nПеревір нік, ID та інтернет."
            )
            self.status.text = "СТАТУС: НЕДОСТУПНИЙ"

    def load_avatar(self):
        try:
            response = requests.get(
                "https://thumbnails.roblox.com/v1/users/avatar"
                f"?userIds={self.user_id}&size=420x420&format=Png",
                timeout=15
            )
            response.raise_for_status()

            url = response.json()["data"][0]["imageUrl"]
            img = requests.get(url, timeout=15)
            img.raise_for_status()

            self.avatar.texture = CoreImage(
                io.BytesIO(img.content),
                ext="png"
            ).texture

        except Exception:
            self.about.text += "\nАватарка недоступна."

    def get_count(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json().get("count", "—")
        except Exception:
            return "—"

    def load_stats(self):
        user = self.user_id

        friends = self.get_count(
            f"https://friends.roblox.com/v1/users/{user}/friends/count"
        )

        followers = self.get_count(
            f"https://friends.roblox.com/v1/users/{user}/followers/count"
        )

        following = self.get_count(
            f"https://friends.roblox.com/v1/users/{user}/followings/count"
        )

        self.stats.text = (
            f"Друзі: {friends}     Підписники: {followers}\n"
            f"Підписки: {following}"
        )

    def check_presence(self):
        try:
            response = requests.post(
                "https://presence.roblox.com/v1/presence/users",
                json={"userIds": [self.user_id]},
                timeout=15
            )
            response.raise_for_status()

            p = response.json()["userPresences"][0]
            status = p["userPresenceType"]

            if status == 2:
                self.status.text = "● ЗАРАЗ У ГРІ"
                self.status.color = (0.3, 1, 0.5, 1)

                self.place_id = p.get("placeId")
                self.game_id = p.get("gameId")

                if self.place_id and self.game_id:
                    self.join.disabled = False

            elif status == 1:
                self.status.text = "● ОНЛАЙН"
                self.status.color = (0.3, 0.65, 1, 1)

            else:
                self.status.text = "● ОФЛАЙН"
                self.status.color = (0.65, 0.65, 0.7, 1)

        except Exception:
            self.status.text = "СТАТУС: НЕДОСТУПНИЙ"

    def copy_id(self, instance):
        if self.user_id:
            Clipboard.copy(str(self.user_id))
            self.info.text += "\nID скопійовано!"

    def open_profile(self, instance):
        if self.user_id:
            webbrowser.open(
                f"https://www.roblox.com/users/{self.user_id}/profile"
            )

    def join_game(self, instance):
        if self.place_id and self.game_id:
            link = (
                "roblox://experiences/start"
                f"?placeId={self.place_id}"
                f"&gameInstanceId={self.game_id}"
            )
            webbrowser.open(link)


RobloxFinder().run()
