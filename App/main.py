__version__ = '1.0'

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from remote import ShoppingList
from remote import reset_lock_on_server

URL = 'insert server address here'


class ScrollableListWidget(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollableListWidget, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.slist = ShoppingListWidget()
        self.add_widget(self.slist)


class ImageButton(ButtonBehavior, Image):
    def __init__(self, source, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.source = source


class MainView(GridLayout):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.cols = 1
        self.slist = ScrollableListWidget()
        self.header = HeaderWidget()
        self.header.size_hint = (1.0, 0.1)
        self.slist.size_hint = (1.0, 0.9)
        self.add_widget(self.header)
        self.add_widget(self.slist)


class HeaderWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(HeaderWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 60
        self.padding = 45
        self.label = Label(on_touch_down=self.create_clock, on_touch_up=self.delete_clock)
        self.label.font_size = '5mm'
        self.label.text = 'GnuBuy'

        self.add_item_popup = InputPopupWidget(callback=self.add_item, title='Add Item')
        self.add_button = ImageButton(size_hint=(0.1, 1.0), source='data/plus.png')
        self.add_button.bind(on_press=self.add_item_popup.open)
        self.add_button.disabled = True
        self.add_button.opacity = 0.0

        self.update_button = ImageButton(source='data/refresh_on.png')
        self.update_button.size_hint = (0.1, 1.0)
        self.edit_button = ImageButton(source='data/edit.png')
        self.update_button.bind(on_release=self.update_list)
        self.edit_button.bind(on_release=self.toggle_edit_mode)
        self.edit_button.size_hint = (0.1, 1.0)
        self.add_widget(self.label)
        self.add_widget(self.add_button)
        self.add_widget(self.update_button)
        self.add_widget(self.edit_button)

    def create_clock(self, label_object, pos):
        if label_object.collide_point(*pos.pos):
            self.clock_event = Clock.schedule_once(self.reset_server, 3)

    def delete_clock(self, label_object, pos):
        if label_object.collide_point(*pos.pos):
            Clock.unschedule(self.clock_event)

    def reset_server(self, inst):
        reset_lock_on_server(URL)

    def update_list(self, inst):
        self.ref_to_slist.update_list_from_server()

    def on_parent(self, screen, parent):
        self.ref_to_slist = parent.slist.slist

    def toggle_edit_mode(self, inst):
        self.ref_to_slist.toggle_edit_mode_server()
        if self.ref_to_slist.edit_mode:
            self.edit_button.source = 'data/edit_on.png'
            self.add_button.opacity = 1.0
            self.add_button.disabled = False
        else:
            self.edit_button.source = 'data/edit.png'
            self.add_button.opacity = 0.0
            self.add_button.disabled = True

    def add_item(self, inst):
        title = self.add_item_popup.input_text
        self.ref_to_slist.add_item(title, 1, True)


class ShoppingListWidget(GridLayout):
    def __init__(self, **kwargs):
        super(ShoppingListWidget, self).__init__(**kwargs)
        self.sl = ShoppingList(URL, debug=True)
        self.edit_mode = False
        self.size_hint = (1, None)
        self.height_item = 0.15 * Window.height
        self.cols = 1
        self.ordered_item_list = []
        self.active_items = []
        self.passive_item = []
        self.update_list_from_server()

    def _update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def update_list_from_server(self):
        self.sl.get_list_from_server()
        if self.sl.request_success:
            self._populate_list()
        else:
            print('Error while syncing')

    def toggle_edit_mode_server(self):
        if self.edit_mode:
            self.sl.lock_and_release_list(False)
            if not self.sl.request_success:
                return
            self.sl.send_list_to_server()
            if not self.sl.request_success:
                return
            self.edit_mode = False
        else:
            self.sl.lock_and_release_list(True)
            if self.sl.request_success:
                self.edit_mode = True

    def _update_item_lists(self):
        self.active_items = [ele for ele in self.sl.items if ele['active']]
        self.passive_items = [ele for ele in self.sl.items if not ele['active']]
        self.ordered_item_list = self.active_items + self.passive_items

    def _add_items(self):
        black = (1.0, 1.0, 1.0, 0.05)
        gray = (1.0, 1.0, 1.0, 0.1)

        for idx, item in enumerate(self.ordered_item_list):
            list_element = ListItemWidget(item, idx)
            list_element.bind(size=self._update_rect, pos=self._update_rect)
            if idx % 2 == 1:
                color = black
            else:
                color = gray
            with list_element.canvas.before:
                Color(*color)
                list_element.rect = Rectangle(size=list_element.size,
                                              pos=list_element.pos)
            self.add_widget(list_element)

    def _populate_list(self):
        self._update_item_lists()
        self.clear_widgets()
        self.height = self.height_item * len(self.ordered_item_list)
        self._add_items()

    def get_id_from_title(self, title):
        return [i for i in range(len(self.sl.items)) if self.sl.items[i]['title'] == title][0]

    def toggle(self, title):
        idx = self.get_id_from_title(title)
        self.sl.items[idx]['active'] = not self.sl.items[idx]['active']
        self._populate_list()

    def change_amount(self, title, new_amount):
        idx = self.get_id_from_title(title)
        self.sl.items[idx]['amount'] = new_amount

    def change_name(self, title, new_name):
        idx = self.get_id_from_title(title)
        self.sl.items[idx]['title'] = new_name
        self._populate_list()

    def add_item(self, title, amount, active):
        item = dict(title=title, amount=amount, active=active)
        self.sl.items.append(item)
        self._populate_list()


class InputPopupWidget:
    def __init__(self, callback=None, title=None):
        if not all([callback, title]):
            raise KeyError('Must provide callback method as well as a title for popup')
        self.title = title
        self.popup_layout = BoxLayout(orientation='vertical')
        self.popup_ok_btn = Button(text='Ok', size_hint=(1.0, 0.6))
        self.popup_text_input = TextInput(text='', multiline=False, size_hint=(1.0, 0.4))
        self.popup_layout.add_widget(self.popup_text_input)
        self.popup_layout.add_widget(self.popup_ok_btn)
        self.popup = Popup(content=self.popup_layout, size_hint=(1.0, 0.3), auto_dismiss=False, title=self.title)
        self.popup_ok_btn.bind(on_press=self.popup.dismiss)
        self.popup.bind(on_dismiss=callback)

    def open(self, _=None):
        self.popup.open()

    @property
    def input_text(self):
        return self.popup_text_input.text


class ListItemWidget(BoxLayout):
    def __init__(self, item, _id, **kwargs):
        super(ListItemWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self._id = _id
        self.spacing = 5
        self.item = item
        self.name = item['title']
        self.amount = item['amount']
        self.spacing = 10
        self.padding = 25
        self.clock_event = None

        self.editing_label = None
        self.popup = InputPopupWidget(callback=self.edit_label, title='Change Item')

        self.label = Label(text=self.name, markup=True, on_touch_down=self.create_clock, on_touch_up=self.delete_clock)
        self.label.font_size = '3mm'
        if not item['active']:
            self.label.text = "[s]%s[/s]" % self.name
            self.label.color = (1, 1, 1, 0.2)
        self.add_widget(self.label)
        self.minus_btn = ImageButton(size_hint=(0.1, 0.6), pos_hint={'top': 0.75}, source='data/minus.png')
        self.minus_btn.bind(on_release=self.decrease_amount)
        self.add_widget(self.minus_btn)
        self.amount_label = Label(text=str(self.amount), size_hint=(0.13, 1.0), font_size='3mm')
        self.add_widget(self.amount_label)
        self.plus_btn = ImageButton(size_hint=(0.1, 0.6), pos_hint={'top': 0.75}, source='data/plus.png')
        self.plus_btn.bind(on_release=self.increase_amount)
        self.add_widget(self.plus_btn)

    def increase_amount(self, _):
        if self.parent.edit_mode:
            self.parent.change_amount(self.name, self.amount + 1)
            self.amount += 1
            self.update_amount()

    def decrease_amount(self, _):
        if self.parent.edit_mode:
            if self.amount > 1:
                self.parent.change_amount(self.name, self.amount - 1)
                self.amount -= 1
                self.update_amount()

    def update_amount(self):
        self.amount_label.text = str(self.amount)

    def create_clock(self, label_object, pos):
        if label_object.collide_point(*pos.pos):
            if self.parent.edit_mode:
                self.editing_label = label_object
                self.clock_event = Clock.schedule_once(self.popup.open, 2)

    def delete_clock(self, label_object, pos):
        if label_object.collide_point(*pos.pos):
            if self.parent.edit_mode:
                Clock.unschedule(self.clock_event)
                self.parent.toggle(self.name)

    def edit_label(self, _):
        self.parent.change_name(self.name, self.popup.input_text)


class NoteApp(App):
    def __init__(self, **kwargs):
        super(NoteApp, self).__init__(**kwargs)
        self.mw = MainView()

    def build(self):
        return self.mw

    def on_close(self):
        #ToDo: Release lock on server
        print('Cloooooosing')


if __name__ == '__main__':
    NoteApp().run()
