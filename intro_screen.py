# intro_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'intro'

        screen_layout = FloatLayout()

        # 1. Arkaplan Resmi
        try:
            background = Image(
                source='images/intro.png',
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            screen_layout.add_widget(background)
        except Exception as e:
            print(f"Intro ekranı arkaplan resmi yüklenemedi: {e}")

        # 2. Üst Buton (Sadece Hakkında Butonu)
        self.hakkinda_button = Button(
            background_normal='images/hakkindaBtn.png',
            background_down='images/hakkindaBtn.png',
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={'right': 1 - (dp(10) / (self.width if self.width else dp(360))), 'top': 0.98},
            border=(0, 0, 0, 0)
        )
        self.hakkinda_button.bind(on_release=self.go_to_about_screen)

        def update_hakkinda_button_position(instance, value):
            current_width = instance.width if instance.width else dp(360)
            if current_width > 0:
                self.hakkinda_button.pos_hint = {'right': 1 - (dp(10) / current_width), 'top': 0.98}

        self.bind(size=update_hakkinda_button_position)
        if self.width:
            update_hakkinda_button_position(self, self.size)

        screen_layout.add_widget(self.hakkinda_button)

        # 3. Orta Giriş Çerçevesi
        self.login_frame = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(300), dp(220)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(20),
            spacing=dp(15)
        )

        with self.login_frame.canvas.before:
            Color(rgba=get_color_from_hex('#ADD8E6AA'))
            self.login_frame_rect = RoundedRectangle(
                size=self.login_frame.size,
                pos=self.login_frame.pos,
                radius=[dp(15)]
            )

        def update_login_frame_rect(instance, value):
            self.login_frame_rect.pos = instance.pos
            self.login_frame_rect.size = instance.size

        self.login_frame.bind(pos=update_login_frame_rect, size=update_login_frame_rect)

        title_label = Label(
            text="Kullanıcı Girişi",
            color=get_color_from_hex('#333333'),
            font_size='20sp',
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        self.username_input = TextInput(
            hint_text="Kullanıcı Adı",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size='16sp',
            padding_y=[(dp(48) - dp(20)) / 2, 0],
            padding_x=[dp(10), dp(10)],
            background_color=get_color_from_hex('#FFFFFFDD'),
            hint_text_color=get_color_from_hex('#777777'),
            foreground_color=get_color_from_hex('#000000')
        )
        giris_button_login_frame = Button(
            text="Giriş",
            size_hint_y=None,
            height=dp(50),
            font_size='18sp',
            background_color=get_color_from_hex('#4CAF50'),
            color=get_color_from_hex('#FFFFFF'),
            background_normal=''
        )
        giris_button_login_frame.bind(on_release=self.login_attempt)

        self.login_frame.add_widget(title_label)
        self.login_frame.add_widget(self.username_input)
        self.login_frame.add_widget(giris_button_login_frame)

        screen_layout.add_widget(self.login_frame)
        self.add_widget(screen_layout)

    def login_attempt(self, instance_button):
        username = self.username_input.text.strip()
        if not username:
            self.show_warning_popup("Kullanıcı adı boş bırakılamaz!")
        else:
            print(f"Kullanıcı adı: {username} ile giriş denemesi başarılı.")
            if self.manager:
                # AnaEkranScreen örneğini al ve kullanıcı adını ayarla
                ana_ekran = self.manager.get_screen('ana_ekran')
                if hasattr(ana_ekran, 'set_username'):
                    ana_ekran.set_username(username)
                else:
                    print("UYARI: AnaEkranScreen'de 'set_username' metodu bulunamadı.")

                self.manager.current = 'ana_ekran'  # Ana ekrana yönlendirme
            else:
                print("ScreenManager bulunamadı, ana ekrana geçilemiyor.")

    def show_warning_popup(self, message, title="Uyarı"):
        popup_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        try:
            popup_width_hint = 0.8
            popup_width = Window.width * popup_width_hint if Window.width and Window.width > 0 else dp(
                360) * popup_width_hint
        except Exception:
            popup_width = dp(360) * 0.8

        popup_label = Label(text=message, halign='center', text_size=(popup_width * 0.9, None))

        popup_button_ok = Button(text="Tamam", size_hint_y=None, height=dp(44))

        popup_content.add_widget(popup_label)
        popup_content.add_widget(popup_button_ok)

        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(popup_width_hint, None),
            height=dp(180)
        )
        popup_button_ok.bind(on_release=popup.dismiss)
        popup.open()

    def go_to_about_screen(self, instance_button):
        if self.manager:
            self.manager.current = 'about'
