# ana_ekran_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

class AnaEkranScreen(Screen):
    username = StringProperty("Misafir")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ana_ekran'

        screen_layout = FloatLayout()

        try:
            background = Image(
                source='images/anaEkran.png',
                allow_stretch=True, keep_ratio=False,
                size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            screen_layout.add_widget(background)
        except Exception as e:
            print(f"Ana ekran arkaplan resmi yüklenemedi: {e}")

        self.welcome_label = Label(
            text=f"Merhaba, {self.username}!",
            size_hint_y=None, height=dp(40), font_size='20sp',
            color=get_color_from_hex('#FFFFFF'), bold=True,
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        self.bind(username=self._update_welcome_text)
        self._update_welcome_text()
        screen_layout.add_widget(self.welcome_label)

        button_layout = BoxLayout(
            orientation='vertical', spacing=dp(25),
            size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        button_width = dp(140)
        button_height = dp(80)
        button_layout.width = button_width
        button_layout.height = (button_height * 3) + (dp(25) * 2)

        buttons_data = [
            {'source': 'images/kelimeCalisBtn.png', 'action_name': 'kelime_calis'},
            {'source': 'images/testBtn.jpeg', 'action_name': 'test_yap'},
            {'source': 'images/veritabaniBtn.png', 'action_name': 'veritabani_yonet'}
        ]

        for btn_data in buttons_data:
            button = Button(
                background_normal=btn_data['source'],
                background_down=btn_data['source'],
                size_hint=(None, None), size=(button_width, button_height),
                border=(0, 0, 0, 0)
            )
            button.action_name = btn_data['action_name']
            button.image_source = btn_data['source']  # Hata ayıklama için saklamıştık, kalabilir
            button.bind(on_release=self.button_action)
            button_layout.add_widget(button)

        screen_layout.add_widget(button_layout)
        self.add_widget(screen_layout)

    def _update_welcome_text(self, *args):
        self.welcome_label.text = f"Merhaba, {self.username}!"

    def set_username(self, name):
        self.username = name

    def button_action(self, instance_button):
        action = instance_button.action_name
        print(f"Buton tıklandı: {action}, Kaynak: {instance_button.image_source}")

        if self.manager:
            if action == 'kelime_calis':
                kelime_calis_ekrani = self.manager.get_screen('kelime_calis_ekrani')
                if hasattr(kelime_calis_ekrani, 'set_user_data'):
                    kelime_calis_ekrani.set_user_data(self.username)
                self.manager.current = 'kelime_calis_ekrani'
            elif action == 'test_yap':
                test_ekrani = self.manager.get_screen('test_ekrani')  # <<< YENİ
                if hasattr(test_ekrani, 'set_user_data'):  # <<< YENİ
                    test_ekrani.set_user_data(self.username)  # <<< YENİ
                self.manager.current = 'test_ekrani'  # <<< YÖNLENDİRME
            elif action == 'veritabani_yonet':
                self.manager.current = 'veritabani_ekrani'
        else:
            print("ScreenManager bulunamadı.")
