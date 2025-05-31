# hakkinda_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'about'
        # Ana layout: Dikey BoxLayout, kenar boşluklu
        self.screen_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Arkaplan Rengi
        with self.screen_layout.canvas.before:
            Color(rgba=get_color_from_hex('#F0F0F0FF'))  # Çok açık gri
            self.bg_rect = Rectangle(size=self.screen_layout.size, pos=self.screen_layout.pos)

        self.screen_layout.bind(size=self._update_bg_rect_size, pos=self._update_bg_rect_pos)

        # ScrollView (metin içeriği için)
        self.scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )
        self.content_layout = BoxLayout(
            orientation='vertical',
            padding=(dp(30), dp(20), dp(30), dp(20)),
            spacing=dp(15),
            size_hint_y=None
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        # Hakkında Metni
        about_text_content = (
            "[size=22sp][b]KELİME CANAVARI UYGULAMASI HAKKINDA[/b][/size]\n\n"
            "•  Bu uygulama Seyfettin DEGER tarafından hazırlanmıştır.\n"
            "•  Bu uygulama Python Programlama Dili ve Kivy Kütüphanesi kullanılarak hazırlanmıştır.\n"
            "•  Bu uygulama android cihazlar için tasarlanmış bir uygulamadır. İngilizce'de en çok kullanılan 5000 kelimeyi ezberlemek için tasarlanmıştır.\n"
            "•  Kelimeleri ezberlemek için Kelime Çalış sayfasında kelimenin hem anlamı hem cümle içindeki kullanımı öğrenebiliyoruz. Böylece kelime zihnimizde daha kalıcı hale geliyor.\n"
            "•  Test ekranını kelimeleri öğrenip öğrenmediğimizi test etmek için kullanabiliyoruz.\n"
            "•  Ayrıca test ekranında bildiğimiz kelimeler Veritabanından siliniyor, böylece bilmediğimiz kelimelere odaklanabiliyoruz.\n"
            "•  Eğer istersek Veritabanı sayfasından orijinal Veritabanını geri yükleyebiliyoruz.\n"
            "•  Veritabanındaki kelimeler 'American Oxford 5000' sitesinden alınmıştır. Adres aşağıdadır.\n"
            "https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/American_Oxford_5000.pdf"
        )

        self.text_label = Label(
            text=about_text_content,
            markup=True,
            font_size='18sp',
            color=get_color_from_hex('#333333'),
            halign='left',
            valign='top',
            size_hint_x=1,
            size_hint_y=None
        )
        self.text_label.bind(width=self._on_text_label_width_changed)  # Genişlik değişimine bağla
        self.content_layout.add_widget(self.text_label)
        self.scroll_view.add_widget(self.content_layout)
        # Geri Dön Butonu
        self.back_button = Button(
            text='Geri Dön',
            size_hint=(1, None),
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=get_color_from_hex('#FFFFFF')
        )
        self.back_button.bind(on_release=self.go_to_intro_screen)

        self.screen_layout.add_widget(self.scroll_view)
        self.screen_layout.add_widget(self.back_button)
        self.add_widget(self.screen_layout)

        Clock.schedule_once(self.force_scroll_to_top, 0.1)
        # İlk text_size ayarını tetiklemek için
        Clock.schedule_once(lambda dt: self._on_text_label_width_changed(self.text_label, self.text_label.width), 0.05)

    def _update_bg_rect_size(self, instance, size):
        if hasattr(self, 'bg_rect') and self.bg_rect:
            self.bg_rect.size = size

    def _update_bg_rect_pos(self, instance, pos):
        if hasattr(self, 'bg_rect') and self.bg_rect:
            self.bg_rect.pos = pos

    def _on_text_label_width_changed(self, instance, width):
        # print(f"TextLabel width changed: {width}")
        if width > 0:
            instance.text_size = (width, None)
            # Yüksekliği bir sonraki frame'de ayarla ki texture güncellenmiş olsun
            Clock.schedule_once(lambda dt: self._set_label_height_from_texture(instance), 0)

    def _set_label_height_from_texture(self, instance):
        # print(f"Attempting to set label height. Texture size: {instance.texture_size}, Current height: {instance.height}")
        if instance.texture_size[1] > 0 and instance.height != instance.texture_size[1]:
            instance.height = instance.texture_size[1]

    def force_scroll_to_top(self, dt):
        if self.scroll_view:
            self.scroll_view.scroll_y = 1.0

    def go_to_intro_screen(self, instance_button):
        if self.manager:
            self.manager.current = 'intro'

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager

    class TestApp(App):
        def build(self):
            Window.size = (dp(360), dp(640))
            sm_test = ScreenManager()
            sm_test.add_widget(AboutScreen(name='about_test'))
            return sm_test

    TestApp().run()
