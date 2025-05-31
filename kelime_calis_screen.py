# kelime_calis_screen.py
import os
import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout  # Kart için
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget  # Spacer için eklendi
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

class FlipCard(ButtonBehavior, RelativeLayout):
    front_image_source = StringProperty('images/cardFront.png')
    back_image_source = StringProperty('images/cardBack.png')

    word_text = StringProperty('')
    example_text = StringProperty('')
    meaning_text = StringProperty('')

    is_front_showing = BooleanProperty(True)
    is_animating = BooleanProperty(False)

    word_label = ObjectProperty(None)
    example_label = ObjectProperty(None)
    meaning_label = ObjectProperty(None)

    front_image = ObjectProperty(None)
    back_image = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_card_flipped_to_back')
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = dp(300)
        self.height = dp(200)

        self.front_image = Image(source=self.front_image_source, size_hint=(1, 1), allow_stretch=True, keep_ratio=False)
        self.back_image = Image(source=self.back_image_source, size_hint=(1, 1), allow_stretch=True, keep_ratio=False,
                                opacity=0)

        front_text_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                      size_hint=(0.9, 0.8))
        self.word_label = Label(text=self.word_text, font_size='24sp', color=(0, 0, 0, 1), bold=True, halign='center',
                                valign='middle', shorten=True, shorten_from='right', text_size=(self.width * 0.8, None))
        self.example_label = Label(text=self.example_text, font_size='16sp', color=(0.2, 0.2, 0.2, 1), halign='center',
                                   valign='top', text_size=(self.width * 0.8, None))

        front_text_layout.add_widget(self.word_label)
        front_text_layout.add_widget(BoxLayout(size_hint_y=0.1))
        front_text_layout.add_widget(self.example_label)

        self.meaning_label = Label(text=self.meaning_text, font_size='22sp', color=(0, 0, 0, 1), bold=True,
                                   halign='center', valign='middle', opacity=0,
                                   text_size=(self.width * 0.8, None),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.add_widget(self.back_image)
        self.add_widget(self.front_image)
        self.add_widget(front_text_layout)
        self.add_widget(self.meaning_label)

        self.bind(word_text=self.update_labels)
        self.bind(example_text=self.update_labels)
        self.bind(meaning_text=self.update_labels)
        self.bind(size=self.update_label_text_sizes)

    def update_label_text_sizes(self, instance, value):
        width, height = value
        if width > 0:
            self.word_label.text_size = (width * 0.8, None)
            self.example_label.text_size = (width * 0.8, None)
            self.meaning_label.text_size = (width * 0.8, None)

    def update_labels(self, instance, value):
        self.word_label.text = self.word_text
        self.example_label.text = self.example_text
        self.meaning_label.text = self.meaning_text

    def on_release(self):
        if not self.is_animating:
            if self.is_front_showing:
                self.flip_to_back()

    def flip_to_back(self):
        self.is_animating = True
        self.is_front_showing = False
        self.front_image.opacity = 0
        self.word_label.opacity = 0
        self.example_label.opacity = 0

        self.back_image.opacity = 1
        self.meaning_label.opacity = 1

        self.dispatch('on_card_flipped_to_back')

    def flip_to_front(self):
        self.is_animating = True
        self.is_front_showing = True
        self.meaning_label.opacity = 0
        self.back_image.opacity = 0

        self.front_image.opacity = 1
        self.word_label.opacity = 1
        self.example_label.opacity = 1
        self.is_animating = False

    def reset_card(self):
        self.meaning_label.opacity = 0
        self.back_image.opacity = 0
        self.front_image.opacity = 1
        self.word_label.opacity = 1
        self.example_label.opacity = 1
        self.is_front_showing = True
        self.is_animating = False

    def on_card_flipped_to_back(self, *args):
        pass


class KelimeCalisScreen(Screen):
    username = StringProperty("Misafir")
    current_word_index = NumericProperty(0)
    total_words = NumericProperty(0)
    word_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'kelime_calis_ekrani'
        screen_layout = FloatLayout()

        try:
            background = Image(source='images/kelimeCalisEkran.png', allow_stretch=True, keep_ratio=False)
            screen_layout.add_widget(background)
        except Exception as e:
            print(f"Kelime Çalış ekranı arkaplan resmi yüklenemedi: {e}")

        top_bar_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            pos_hint={'top': 0.98},
            padding=(dp(10), dp(5), dp(10), dp(5)),
            spacing=dp(5)
        )

        self.home_button = Button(
            background_normal='images/anasayfaBtn.png',
            size_hint=(None, 1),
            width=dp(44),
            border=(0, 0, 0, 0)
        )
        self.home_button.bind(on_release=self.go_to_home_screen)

        self.player_label = Label(
            text=f"Oyuncu: {self.username}",
            font_size='16sp',
            color=get_color_from_hex('#FFFFFF'),
            halign='left', valign='middle',
            size_hint_x=None,
            width=dp(150)
        )
        self.word_count_label = Label(
            text=f"Kelime: 0/0",
            font_size='16sp',
            color=get_color_from_hex('#FFFFFF'),
            halign='right', valign='middle',
            size_hint_x=None,
            width=dp(100)
        )

        self.player_label.bind(width=lambda instance, width_val: setattr(instance, 'text_size', (width_val, None)))
        self.word_count_label.bind(width=lambda instance, width_val: setattr(instance, 'text_size', (width_val, None)))

        top_bar_layout.add_widget(self.home_button)
        top_bar_layout.add_widget(self.player_label)
        top_bar_layout.add_widget(Widget(size_hint_x=1))
        top_bar_layout.add_widget(self.word_count_label)
        screen_layout.add_widget(top_bar_layout)

        self.flip_card = FlipCard(pos_hint={'center_x': 0.5, 'center_y': 0.53})
        self.flip_card.bind(on_card_flipped_to_back=self.handle_card_flip_to_back)
        screen_layout.add_widget(self.flip_card)

        nav_button_layout = BoxLayout(
            size_hint=(0.8, None), height=dp(60),
            pos_hint={'center_x': 0.5},
            y=dp(80),
            spacing=dp(50)
        )

        self.prev_button = Button(background_normal='images/oncekiKelimeBtn.png', size_hint=(None, None),
                                  size=(dp(100), dp(60)), border=(0, 0, 0, 0))
        self.next_button = Button(background_normal='images/sonrakiKelimeBtn.png', size_hint=(None, None),
                                  size=(dp(100), dp(60)), border=(0, 0, 0, 0))

        self.prev_button.bind(on_release=self.show_previous_word)
        self.next_button.bind(on_release=self.show_next_word)

        nav_button_layout.add_widget(BoxLayout(size_hint_x=1))
        nav_button_layout.add_widget(self.prev_button)
        nav_button_layout.add_widget(BoxLayout(size_hint_x=0.5))
        nav_button_layout.add_widget(self.next_button)
        nav_button_layout.add_widget(BoxLayout(size_hint_x=1))
        screen_layout.add_widget(nav_button_layout)

        self.add_widget(screen_layout)

        self.bind(on_enter=self._on_screen_enter)
        self.bind(on_leave=self._on_screen_leave)
        self.bind(username=lambda instance, value: setattr(self.player_label, 'text', f"Oyuncu: {value}"))

    def _on_screen_enter(self, *args):
        print("KelimeCalisScreen: on_enter çağrıldı.")
        self.load_words_from_db()

    def _on_screen_leave(self, *args):
        print("KelimeCalisScreen: on_leave çağrıldı.")
        pass

    def load_words_from_db(self, *args):
        db_file_name = "veritabani.db"
        if not os.path.exists(db_file_name):
            print(f"Hata: Veritabanı dosyası '{db_file_name}' bulunamadı.")
            self.word_list = []
            self.total_words = 0
            self.current_word_index = -1
            self.update_display()
            return

        try:
            conn = sqlite3.connect(db_file_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, kelime, anlam, ornek_cumle FROM kelimeler ORDER BY id")
            self.word_list = cursor.fetchall()
            conn.close()
            self.total_words = len(self.word_list)
            if self.total_words > 0:
                self.current_word_index = 0
            else:
                self.current_word_index = -1
            print(f"{self.total_words} kelime veritabanından yüklendi.")
        except sqlite3.Error as e:
            print(f"Veritabanı okuma hatası: {e}")
            self.word_list = []
            self.total_words = 0
            self.current_word_index = -1

        self.update_display()

    def update_display(self):
        if 0 <= self.current_word_index < self.total_words:
            current_word_data = self.word_list[self.current_word_index]
            self.flip_card.word_text = str(current_word_data[1] if current_word_data[1] is not None else "")
            self.flip_card.meaning_text = str(current_word_data[2] if current_word_data[2] is not None else "")
            self.flip_card.example_text = str(current_word_data[3] if current_word_data[3] is not None else "")
            self.word_count_label.text = f"Kelime: {self.current_word_index + 1}/{self.total_words}"
            self.flip_card.reset_card()
        else:
            self.flip_card.word_text = "Kelime Yok"
            self.flip_card.meaning_text = ""
            self.flip_card.example_text = "Veritabanında kelime bulunamadı."
            self.word_count_label.text = f"Kelime: 0/{self.total_words}"
            self.flip_card.reset_card()

        self.prev_button.disabled = not (self.total_words > 0 and self.current_word_index > 0)
        self.next_button.disabled = not (self.total_words > 0 and self.current_word_index < self.total_words - 1)

    def handle_card_flip_to_back(self, instance_card):
        print("Kart arka yüze döndü, anlam gösteriliyor.")
        Clock.schedule_once(lambda dt: self.flip_card.flip_to_front(), 1)  # Anlam 1 saniye görünür kalır

    def show_previous_word(self, instance_button):
        if self.total_words > 0 and self.current_word_index > 0:
            self.current_word_index -= 1
            self.update_display()

    def show_next_word(self, instance_button):
        if self.total_words > 0 and self.current_word_index < self.total_words - 1:
            self.current_word_index += 1
            self.update_display()

    def set_user_data(self, username):
        self.username = username

    def go_to_home_screen(self, instance_button):
        if self.manager:
            self.manager.current = 'ana_ekran'

    def on_stop_app(self):
        print("KelimeCalisScreen: on_stop_app çağrıldı (TTS yok).")
        pass

