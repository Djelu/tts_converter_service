from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.pagelayout import PageLayout
from kivy.utils import get_color_from_hex

from tts_converter import TtsConverter

Config.set("graphics", "width", "420")
Config.set("graphics", "height", "720")

converter = TtsConverter()
   
class PageLayout(PageLayout):
    def __init__(self):
        super(PageLayout, self).__init__()
        verticalBox = BoxLayout(orientation='vertical')
        verticalBox.spacing = 30
        verticalBox.padding = [30, 30, 30, 30]
        
        p1_btn1 = Button(text ="Переделать все книги", on_press = self.start_convert)
        p1_btn1.background_color = get_color_from_hex("#444444")

        p1_btn2 = Button(text ="Переделать без склеивания", on_press = self.start_convert_not_full)
        p1_btn2.background_color = get_color_from_hex("#444444")
        
        p1_btn3 = Button(text ="Выход", on_press = self.exit_press)
        p1_btn3.background_color = get_color_from_hex("#444444")

        btn2 = Button(text ="Page 2", on_press = self.btn_press)
        btn2.background_color = get_color_from_hex("#000000")
        btn3 = Button(text ="Page 3", on_press = self.btn_press)
        btn3.background_color = get_color_from_hex("#333333")

        verticalBox.add_widget(p1_btn1)
        verticalBox.add_widget(p1_btn2)
        verticalBox.add_widget(p1_btn3)
        self.add_widget(verticalBox)
        self.add_widget(btn2)
        self.add_widget(btn3)

    def btn_press(self, instance):
        print("btn_press: " + instance.text )

    def start_convert(self, instance):
        converter.SAVE_AUDIOBOOKS_FULL = True
        converter.convert()
        
    def start_convert_not_full(self, instance):
        converter.SAVE_AUDIOBOOKS_FULL = False
        converter.convert()
        
    def exit_press(self, instance):
        EdgeTtsApp.Exit()
 
class EdgeTtsApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.05)
        return PageLayout()
  
if __name__ == '__main__':
    EdgeTtsApp().run()