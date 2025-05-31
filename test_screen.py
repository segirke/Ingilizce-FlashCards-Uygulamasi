# test_screen.py
import os
import sqlite3
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

class TestScreen(Screen):
    username = StringProperty("Misafir")
    status_message = StringProperty("")

    current_word_data = ListProperty([None, None, None, None])
    current_meaning_to_display = StringProperty("")
    options = ListProperty([])
    correct_answer_english = StringProperty("")

    available_words = ListProperty([])
    total_initial_words = NumericProperty(0)
    words_to_test_count = NumericProperty(0)

    option_buttons = []

    # Ses efektleri için
    correct_sound = ObjectProperty(None, allownone=True)
    wrong_sound = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'test_ekrani'
        self._load_sounds()  # Sesleri yükle

        screen_layout = FloatLayout()

        try:
            background = Image(source='images/test.png', allow_stretch=True, keep_ratio=False)
            screen_layout.add_widget(background)
        except Exception as e:
            print(f"Test ekranı arkaplan resmi yüklenemedi: {e}")
            with screen_layout.canvas.before:
                Color(rgba=get_color_from_hex('#E0F2F7FF'))
                self.bg_rect = Rectangle(size=screen_layout.size, pos=screen_layout.pos)
            screen_layout.bind(size=lambda i, s: setattr(self.bg_rect, 'size', s),
                               pos=lambda i, p: setattr(self.bg_rect, 'pos', p))

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
            color=get_color_from_hex('#F0F0F0'),
            halign='left', valign='middle',
            size_hint_x=0.6
        )
        self.progress_label = Label(
            text="Kalan: 0",
            font_size='16sp',
            color=get_color_from_hex('#F0F0F0'),
            halign='right', valign='middle',
            size_hint_x=0.4
        )

        self.player_label.bind(
            width=lambda i, w: setattr(i, 'text_size', (w - dp(5), None) if w > dp(5) else (0, None)))
        self.progress_label.bind(
            width=lambda i, w: setattr(i, 'text_size', (w - dp(5), None) if w > dp(5) else (0, None)))

        top_bar_layout.add_widget(self.home_button)
        top_bar_layout.add_widget(self.player_label)
        top_bar_layout.add_widget(self.progress_label)
        screen_layout.add_widget(top_bar_layout)

        self.meaning_display_label = Label(
            text="",
            font_size='30sp',
            color=get_color_from_hex('#222222'),
            bold=True,
            size_hint=(0.8, None),
            height=dp(60),
            pos_hint={'center_x': 0.5, 'top': 0.82},
            halign='center',
            valign='middle'
        )
        self.meaning_display_label.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))
        screen_layout.add_widget(self.meaning_display_label)

        self.options_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint=(None, None),
            width=dp(280),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )
        screen_layout.add_widget(self.options_layout)

        self.feedback_label = Label(
            text="",
            font_size='18sp',
            color=get_color_from_hex('#111111'),
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_x': 0.5, 'y': dp(100)}
        )
        screen_layout.add_widget(self.feedback_label)

        self.add_widget(screen_layout)

        self.bind(on_enter=self.start_test)
        self.bind(username=lambda i, val: setattr(self.player_label, 'text', f"Oyuncu: {val}"))

    def _load_sounds(self):
        """Ses dosyalarını yükler."""
        try:
            self.correct_sound = SoundLoader.load('sounds/dogruSes.wav')
            if self.correct_sound:
                print("Doğru cevap sesi yüklendi.")
            else:
                print("UYARI: 'sounds/dogruSes.wav' yüklenemedi.")
        except Exception as e:
            print(f"Doğru cevap sesi yüklenirken hata: {e}")
            self.correct_sound = None

        try:
            self.wrong_sound = SoundLoader.load('sounds/yanlisSes.wav')
            if self.wrong_sound:
                print("Yanlış cevap sesi yüklendi.")
            else:
                print("UYARI: 'sounds/yanlisSes.wav' yüklenemedi.")
        except Exception as e:
            print(f"Yanlış cevap sesi yüklenirken hata: {e}")
            self.wrong_sound = None

    def start_test(self, *args):
        print("TestScreen: start_test çağrıldı.")
        self.load_available_words()
        if self.available_words:
            self.total_initial_words = len(self.available_words)
            self.words_to_test_count = len(self.available_words)
            self._next_question()
        else:
            self.meaning_display_label.text = "Test Edilecek Kelime Kalmadı!"
            self.options_layout.clear_widgets()
            self.progress_label.text = "Kalan: 0"
            self.show_congratulations_popup("Tüm kelimeleri öğrendiniz!")

    def load_available_words(self):
        db_file_name = "veritabani.db"
        if not os.path.exists(db_file_name):
            print(f"Hata: Veritabanı dosyası '{db_file_name}' bulunamadı.")
            self.available_words = []
            self.words_to_test_count = 0
            self.progress_label.text = f"Kalan: {self.words_to_test_count}"
            return

        try:
            conn = sqlite3.connect(db_file_name)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, kelime, anlam, ornek_cumle FROM kelimeler WHERE kelime IS NOT NULL AND kelime != ''")
            self.available_words = [list(word) for word in cursor.fetchall() if word[1] and str(word[1]).strip()]
            conn.close()
            random.shuffle(self.available_words)
            print(f"{len(self.available_words)} geçerli kelime test için veritabanından yüklendi.")
        except sqlite3.Error as e:
            print(f"Veritabanı okuma hatası (TestScreen): {e}")
            self.available_words = []

        self.words_to_test_count = len(self.available_words)
        self.progress_label.text = f"Kalan: {self.words_to_test_count}"

    def _next_question(self):
        self.feedback_label.text = ""
        print(f"DEBUG: _next_question. Kalan kelime sayısı: {len(self.available_words)}")

        if not self.available_words:
            self.meaning_display_label.text = "Tebrikler!"
            self.options_layout.clear_widgets()
            self.progress_label.text = "Bitti!"
            self.show_congratulations_popup("Tüm kelimeleri doğru bildiniz!")
            return

        self.current_word_data = self.available_words[0]

        word_id, eng_word, meaning, _ = self.current_word_data

        self.current_meaning_to_display = str(meaning if meaning is not None and str(meaning).strip() else "Anlam Yok")
        self.correct_answer_english = str(eng_word).strip()

        if not self.correct_answer_english:
            print(f"UYARI: Test için seçilen kelime boş (ID: {word_id}). Bu kelime atlanıyor.")
            self.available_words.pop(0)
            self.words_to_test_count = len(self.available_words)
            Clock.schedule_once(lambda dt: self._next_question(), 0)
            return

        print(
            f"DEBUG: Yeni soru: ID={word_id}, Anlam='{self.current_meaning_to_display}', Doğru Cevap='{self.correct_answer_english}'")
        self.meaning_display_label.text = self.current_meaning_to_display

        options_set = set()
        options_set.add(self.correct_answer_english)

        try:
            conn = sqlite3.connect("veritabani.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT kelime FROM kelimeler WHERE id != ? AND kelime IS NOT NULL AND kelime != '' AND kelime != ?",
                (word_id, self.correct_answer_english))
            all_other_valid_words = [str(row[0]).strip() for row in cursor.fetchall() if str(row[0]).strip()]
            conn.close()

            random.shuffle(all_other_valid_words)

            for distractor in all_other_valid_words:
                if len(options_set) >= 5:
                    break
                options_set.add(distractor)

        except sqlite3.Error as e:
            print(f"Yanlış şıklar için veritabanı okuma hatası: {e}")

        idx = 1
        temp_placeholders = []
        while len(options_set) + len(temp_placeholders) < 5:
            placeholder_option = f"Seçenek {idx}"
            is_unique_placeholder = True
            if placeholder_option in options_set:
                is_unique_placeholder = False
            for tp in temp_placeholders:
                if tp == placeholder_option:
                    is_unique_placeholder = False
                    break
            if is_unique_placeholder:
                temp_placeholders.append(placeholder_option)
            idx += 1
            if idx > 20:
                print("UYARI: Şık oluşturmada (placeholder) sonsuz döngüden çıkıldı.")
                break

        for tp in temp_placeholders:
            options_set.add(tp)

        self.options = list(options_set)
        while len(self.options) < 5:
            self.options.append(f"EkstraSeçenek{len(self.options)}")
        self.options = self.options[:5]

        random.shuffle(self.options)

        print(f"DEBUG: Oluşturulan şıklar: {self.options}")
        if self.correct_answer_english not in self.options:
            print(f"KRİTİK HATA: Doğru cevap '{self.correct_answer_english}' son şıklarda YOK: {self.options}")
            if len(self.options) == 5:
                print("KRİTİK HATA DÜZELTME: Doğru cevap şıklara zorla ekleniyor.")
                try:
                    self.options.remove(self.correct_answer_english)
                except ValueError:
                    pass
                if len(self.options) >= 5:
                    self.options.pop()
                self.options.append(self.correct_answer_english)
                while len(self.options) < 5:
                    self.options.append(f"Doldurma{len(self.options)}")
                random.shuffle(self.options)
                self.options = self.options[:5]
                print(f"KRİTİK HATA DÜZELTME SONRASI: Şıklar: {self.options}")

        self._populate_option_buttons()
        self.progress_label.text = f"Kalan: {self.words_to_test_count}"

    def _populate_option_buttons(self):
        self.options_layout.clear_widgets()
        self.option_buttons = []
        num_options = len(self.options)
        if num_options > 0:
            self.options_layout.height = dp(60) * num_options + dp(10) * (max(0, num_options - 1))
        else:
            self.options_layout.height = 0

        for option_text in self.options:
            btn = Button(
                text=str(option_text),
                size_hint_y=None,
                height=dp(60),
                background_color=get_color_from_hex('#FFA726'),
                color=get_color_from_hex('#FFFFFF'),
                font_size='18sp'
            )
            btn.bind(on_release=self.check_answer)
            self.options_layout.add_widget(btn)
            self.option_buttons.append(btn)

    def check_answer(self, instance_button):
        selected_answer = instance_button.text
        if not self.current_word_data or self.current_word_data[0] is None:
            print("HATA: Geçerli kelime verisi yok, cevap kontrol edilemiyor.")
            return

        if selected_answer == self.correct_answer_english:
            self.feedback_label.text = "Doğru!"
            self.feedback_label.color = get_color_from_hex('#4CAF50')
            if self.correct_sound:  # <<< SES ÇALMA
                self.correct_sound.play()

            word_id_to_delete = self.current_word_data[0]
            print(f"DEBUG: Doğru cevap! Silinecek Kelime ID: {word_id_to_delete}")
            self.delete_word_from_db(word_id_to_delete)

            self.available_words = [word for word in self.available_words if word[0] != word_id_to_delete]

            self.words_to_test_count = len(self.available_words)

            self.meaning_display_label.text = "Yükleniyor..."

            Clock.schedule_once(lambda dt: self._next_question(), 1)
        else:
            self.feedback_label.text = "Yanlış! Tekrar Çalışın."
            self.feedback_label.color = get_color_from_hex('#F44336')
            if self.wrong_sound:  # <<< SES ÇALMA
                self.wrong_sound.play()

            # Yanlış cevapta Kelime Çalış ekranına yönlendir
            Clock.schedule_once(self.go_to_kelime_calis, 1.5)  # Sesin bitmesi için kısa bir bekleme

    def go_to_kelime_calis(self, dt):  # <<< YANLIŞ CEVAP İÇİN YENİ METOD
        """Kelime Çalış ekranına yönlendirir."""
        if self.manager:
            self.manager.current = 'kelime_calis_ekrani'

    def delete_word_from_db(self, word_id):
        db_file_name = "veritabani.db"
        if not os.path.exists(db_file_name):
            print(f"Hata: Veritabanı dosyası '{db_file_name}' bulunamadı (silme işlemi).")
            return
        if word_id is None:
            print("HATA: Silinecek kelime ID'si None.")
            return
        try:
            conn = sqlite3.connect(db_file_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kelimeler WHERE id = ?", (word_id,))
            conn.commit()
            conn.close()
            print(f"Kelime ID {word_id} veritabanından silindi.")
        except sqlite3.Error as e:
            print(f"Veritabanından kelime silme hatası: {e}")

    def show_congratulations_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        congrats_label = Label(text=message, font_size='20sp', halign='center')
        ok_button = Button(text="Tamam", size_hint_y=None, height=dp(50))

        content.add_widget(congrats_label)
        content.add_widget(ok_button)

        popup = Popup(title="Test Bitti!", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        ok_button.bind(on_release=lambda x: (popup.dismiss(), self.go_to_home_screen()))
        popup.open()

    def set_user_data(self, username):
        self.username = username

    def go_to_home_screen(self, *args):
        if self.manager:
            self.manager.current = 'ana_ekran'
