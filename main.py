# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.metrics import dp
# Ekranları kendi dosyalarından import et
from intro_screen import IntroScreen
from hakkinda_screen import AboutScreen
from ana_ekran_screen import AnaEkranScreen
from veritabani_screen import VeritabaniScreen
from kelime_calis_screen import KelimeCalisScreen
from test_screen import TestScreen


# Ana Uygulama Sınıfı
class MobilUygulamaApp(App):
    def build(self):
        Window.size = (dp(360), dp(640))

        sm = ScreenManager(transition=FadeTransition(duration=0.3))

        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(AnaEkranScreen(name='ana_ekran'))
        sm.add_widget(VeritabaniScreen(name='veritabani_ekrani'))
        sm.add_widget(KelimeCalisScreen(name='kelime_calis_ekrani'))
        sm.add_widget(TestScreen(name='test_ekrani'))

        return sm

    def on_stop(self):
        """Uygulama kapatıldığında çağrılır."""
        print("Uygulama durduruluyor...")
        if self.root and self.root.has_screen('kelime_calis_ekrani'):
            kelime_calis_screen = self.root.get_screen('kelime_calis_ekrani')
            if hasattr(kelime_calis_screen, 'on_stop_app'):
                kelime_calis_screen.on_stop_app()
        print("Uygulama durdurma işlemleri tamamlandı.")

if __name__ == '__main__':
    MobilUygulamaApp().run()
