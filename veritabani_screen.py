# veritabani_screen.py
import os
import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty

class VeritabaniScreen(Screen):
    status_message = StringProperty("Durum: Bekleniyor...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'veritabani_ekrani'

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        title_label = Label(
            text="Veritabanı Yönetimi",
            font_size='26sp',
            size_hint_y=None,
            height=dp(55),
            color=get_color_from_hex('#E0E0E0'),
            bold=True
        )
        layout.add_widget(title_label)

        restore_button = Button(
            text="Orijinal Veritabanını Geri Yükle",
            size_hint_y=None,
            height=dp(60),
            font_size='18sp',
            background_color=get_color_from_hex('#FF9800'),
            color=get_color_from_hex('#FFFFFF')
        )
        restore_button.bind(on_release=self.confirm_restore_database)
        layout.add_widget(restore_button)

        self.status_label = Label(
            text=self.status_message,
            font_size='16sp',
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex('#555555')
        )
        self.bind(status_message=self.status_label.setter('text'))
        layout.add_widget(self.status_label)

        layout.add_widget(BoxLayout(size_hint_y=1))

        back_button = Button(
            text="Ana Ekrana Dön",
            size_hint_y=None,
            height=dp(50),
            font_size='18sp',
            background_color=get_color_from_hex('#2196F3'),
            color=get_color_from_hex('#FFFFFF')
        )
        back_button.bind(on_release=self.go_to_main_screen)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def confirm_restore_database(self, instance_button):
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        message = Label(
            text="Mevcut çalışma veritabanı silinecek ve\n"
                 "orijinal kelimelerle yeniden yüklenecektir.\nEmin misiniz?",
            halign='center'
        )
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_yes = Button(text="Evet, Geri Yükle")
        btn_no = Button(text="Hayır, İptal Et")

        buttons_layout.add_widget(btn_yes)
        buttons_layout.add_widget(btn_no)

        content.add_widget(message)
        content.add_widget(buttons_layout)

        popup = Popup(title="Onay", content=content, size_hint=(0.8, None), height=dp(220))

        btn_yes.bind(on_release=lambda x: (self.restore_database_from_master(), popup.dismiss()))
        btn_no.bind(on_release=popup.dismiss)

        popup.open()

    def restore_database_from_master(self, *args):
        original_db_name = "orijinal_kelimeler.db"  # Ana veritabanı
        active_db_name = "veritabani.db"  # Uygulamanın kullandığı çalışma veritabanı
        data_folder = "data"

        original_db_path = os.path.join(data_folder, original_db_name)

        self.status_message = "İşlem başlatılıyor..."

        if not os.path.exists(data_folder):
            self.status_message = f"Hata: '{data_folder}' klasörü bulunamadı!"
            print(self.status_message)
            return

        if not os.path.exists(original_db_path):
            self.status_message = f"HATA: Orijinal veritabanı '{original_db_path}' bulunamadı!\nLütfen önce excel_to_sqlite_converter.py scriptini çalıştırın."
            print(self.status_message)
            return

        try:
            self.status_message = "Orijinal veritabanından veriler okunuyor..."
            conn_orig = sqlite3.connect(original_db_path)
            cursor_orig = conn_orig.cursor()
            # Sütun adlarını doğru aldığınızdan emin olun (excel_to_sqlite_converter.py'deki gibi)
            cursor_orig.execute("SELECT kelime, anlam, ornek_cumle FROM kelimeler")
            all_original_words = cursor_orig.fetchall()
            conn_orig.close()

            if not all_original_words:
                self.status_message = "Orijinal veritabanında hiç kelime bulunamadı."
                print(self.status_message)
                return

            self.status_message = "Çalışma veritabanına bağlanılıyor..."
            conn_active = sqlite3.connect(active_db_name)
            cursor_active = conn_active.cursor()

            self.status_message = "Çalışma tablosu oluşturuluyor/temizleniyor..."
            cursor_active.execute('''
                CREATE TABLE IF NOT EXISTS kelimeler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kelime TEXT UNIQUE NOT NULL,
                    anlam TEXT,
                    ornek_cumle TEXT
                )
            ''')
            cursor_active.execute("DELETE FROM kelimeler")
            conn_active.commit()

            self.status_message = "Veriler çalışma veritabanına aktarılıyor..."
            cursor_active.executemany("INSERT OR IGNORE INTO kelimeler (kelime, anlam, ornek_cumle) VALUES (?, ?, ?)",
                                      all_original_words)
            conn_active.commit()

            cursor_active.execute("SELECT COUNT(*) FROM kelimeler")
            rows_in_active_db = cursor_active.fetchone()[0]
            self.status_message = f"Başarılı: {rows_in_active_db} kelime çalışma veritabanına yüklendi."

            conn_active.close()
            print(self.status_message)

        except sqlite3.Error as e:
            self.status_message = f"SQLite Hatası: {e}"
            print(f"SQLite Hatası: {e}")
        except Exception as e:
            self.status_message = f"Bilinmeyen bir hata oluştu: {e}"
            print(f"Genel Hata: {e}")

    def go_to_main_screen(self, instance_button):
        if self.manager:
            self.manager.current = 'ana_ekran'
