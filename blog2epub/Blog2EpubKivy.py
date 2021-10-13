from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class StyledLabel(Label):

    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.size_hint = kwargs.get('size_hint', (0.125, 0.10))


class StyledTextInput(TextInput):

    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.halign = 'center'
        self.valign = 'middle'
        self.size_hint = kwargs.get('size_hint', (0.25, 0.10))


class StyledButton(Button):

    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.size_hint = kwargs.get('size_hint', (0.25, 0.10))


class Blog2EpubKivyWindow(StackLayout):

    def __init__(self, **kwargs):
        super(Blog2EpubKivyWindow, self).__init__(**kwargs)
        self.orientation = 'lr-tb'
        self.padding = 10
        self.spacing = 10

        self.add_widget(StyledLabel(text='Url:'))
        self.url_entry = StyledTextInput(size_hint=(0.625, 0.10))
        self.add_widget(self.url_entry)
        self.download_button = StyledButton(text='Download')
        self.add_widget(self.download_button)

        self.add_widget(StyledLabel(text='Limit:'))
        self.limit_entry = StyledTextInput()
        self.add_widget(self.limit_entry)

        self.add_widget(StyledLabel(text='Skip:'))
        self.skip_entry = StyledTextInput()
        self.add_widget(self.skip_entry)

        self.about_button = StyledButton(text='About')
        self.add_widget(self.about_button)

        self.console_output = TextInput(font_size='15sp', font_name='RobotoMono-Regular', size_hint=(1, 0.8))
        self.add_widget(self.console_output)



class Blog2EpubKivy(App):

    def build(self):
        return Blog2EpubKivyWindow()
