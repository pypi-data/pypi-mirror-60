import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_string('''
WindowManager:
    MainWindow:
    SecondWindow:
    
<MainWindow>:
    name: "main"

    GridLayout:
        cols: 1

        GridLayout:
            cols: 2

            Label:
                text: "Password: "

            TextInput:
                id: passw
                multiline: False

        Button:
            text: "Submit"
            on_release:
                app.root.current = "second"
                root.manager.transition.direction = "left"

<SecondWindow>:
    name: "second"

    Button:
        text: "Go Back"
        on_release:
            app.root.current = "main"
            root.manager.transition.direction = "right"
''')


class MyMainApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    MyMainApp().run()
