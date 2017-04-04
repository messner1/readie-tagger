from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider

from kivy.base import runTouchApp


from kivy.core.window import Window

from kivy.properties import ListProperty
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.popup import Popup

from kivy.uix.floatlayout import FloatLayout

import os
import csv
import sys

import string


Builder.load_string('''

<MainLayout>
	BoxLayout:
		id: topbar
		size_hint_y: 0.05
		pos_hint_y: 0
		padding_bottom: 10



	BoxLayout:
		id: splitcolumns
		orientation: "horizontal"

		BoxLayout:
			id: textlines
			orientation: "vertical"

		BoxLayout:
			id: taglines
			orientation: "vertical"



<ScrollableLabel>:
    Label:
    	id: text_contents
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
        color: root.color

<MainMenu>:
	Button:
		text: 'Load'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.load()

	Button:
		text: 'Save'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.save()

	Button:
		text: 'Add Tag'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.add_tag()

	Button:
		text: 'Load Tags'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.load_tags()

	Button:
		text: 'Export Tags'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.export_tags()

	Button:
		text: 'Jump to Untagged'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.jump_untagged()

	Button:
		text: 'Change Lines/Page'
		size_hint_y: None
		height: self.texture_size[1]
		on_release: root.change_lines_page()


<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserIconView:
            id: filechooser
            filters: ["*.csv"]

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<SaveDialog>:
	text_input: text_input
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserIconView:
            id: filechooser
            on_selection: text_input.text = self.selection and self.selection[0] or ''


        TextInput:
            id: text_input
            size_hint_y: None
            height: 30
            multiline: False

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Save"
                on_release: root.save(filechooser.path, text_input.text)

                

<NumberLinesPageSlider>:
	BoxLayout:
		spacing: 10
		orientation: "vertical"
		size: root.size
		pos: root.pos
		Slider:
			id: lineslider
			min: 0
			max: 10
			value: root.value
			step: 1

		Label:
			text: str(int(lineslider.value))

		Button:
			text: "Accept"
			on_release: root.change_max_value(lineslider.value)

<AddTagDialog>
	text_input: tagname
	BoxLayout:
		spacing: 10
		orientation: "vertical"
		size: root.size
		pos: root.pos
		Label:
			text: "Tag Name:"
		TextInput:
			id: tagname
			multiline: False
            size_hint_y: None
            height: 30

        Label:
        	text:"Tag Key:"
		TextInput:
			id: keyname
			multiline:False
            size_hint_y: None
            height: 30

        BoxLayout:
        	Button:
        		text: "OK"
        		on_release: root.ok(keyname.text,tagname.text)

        	Button:
        		text: "Cancel"
        		on_release: root.cancel()


''')

class MainLayout(BoxLayout):
	pass


class AddTagDialog(FloatLayout):
	ok = ObjectProperty(None)
	cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class NumberLinesPageSlider(FloatLayout):
	value = NumericProperty(5)
	change_max_value = ObjectProperty(None)

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ScrollableLabel(ScrollView):
    text = StringProperty('')
    color = ListProperty()
    last_color = ListProperty()



class MainMenu(DropDown):
	load = ObjectProperty(None)
	save = ObjectProperty(None)
	add_tag = ObjectProperty(None)
	load_tags = ObjectProperty(None)
	jump_untagged = ObjectProperty(None)
	change_lines_page = ObjectProperty(None)
	export_tags = ObjectProperty(None)


class ScrollApp(App):


	#keyboard handling
	def __init__(self, **kwargs):
		super(ScrollApp, self).__init__(**kwargs)

		self.tag_key_pairs = {}

		self.color_labeled = [.93,.14,.14,1]
		self.color_unlabeled = [1,1,1,1]
		self.color_selected = [.93,.80,.14,1]

		self.selected_line_widget = None
		self.lines = []
		self.labels = []
		self.label_widgets = []
		self.line_widgets = []
		self.num_lines_screen = 5
		self.current_index = 0

		self.loaded_path = ""
		self.loaded_filename = ""

		

		self.key_lookup = dict(zip(range(97,123), list(string.lowercase)))

		#self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		Window.bind(on_key_down=self._on_keyboard_down)

		

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers, what):


		if keycode == 274: #down
			self.current_index += self.num_lines_screen
			self.remove_lines_screen()
			self.add_labels_num_lines_screen()
			self.add_tag_labels_num_lines_screen()
		elif keycode == 273: #up
			if self.current_index - self.num_lines_screen < 0:
				self.current_index = 0
			else:
				self.current_index -= self.num_lines_screen
			
			self.remove_lines_screen()
			self.add_labels_num_lines_screen()
			self.add_tag_labels_num_lines_screen()
		#49-57

		elif keycode in range(49,58):
			self.select_lineno(keycode-48) #blah
		elif keycode in self.key_lookup.keys():
			self.tag_line(self.key_lookup[keycode])


		return True


	#csv functions

	def clear_current_csv(self):
		self.lines = []
		self.labels = []
		self.current_index = 0
		self.selected_line_widget = None


	def load_classification_csv(self, file):
		#clear if something already loaded
		self.remove_lines_screen()
		self.clear_current_csv()



		readin = csv.reader(file, delimiter = '\t')
		for line in readin:
			if len(line) > 1:
				self.lines.append(line[0])
				self.labels.append(line[1])
			elif len(line) == 0:
				pass
			else:
				self.lines.append(line[0])
				self.labels.append('')

		self.add_labels_num_lines_screen()
		self.add_tag_labels_num_lines_screen()


	#functions for adding and removing lines of text from the screen

	def remove_lines_screen(self):
		self.selected_line_widget = None #reset selected line
		for line in self.line_widgets:
			self.layout.ids.textlines.remove_widget(line)
		for tag in self.label_widgets:
			self.layout.ids.taglines.remove_widget(tag)

		self.label_widgets = []
		self.line_widgets = []

	def add_line_label(self, line, label):
		self.line_widgets.append(ScrollableLabel(text = line, color = self.color_labeled))
			

		self.line_widgets[-1].last_color = self.line_widgets[-1].color

		self.layout.ids.textlines.add_widget(self.line_widgets[-1])

	def add_labels_num_lines_screen(self):
		for num in range(self.current_index, self.current_index+self.num_lines_screen):
			self.add_line_label(self.lines[num], self.labels[num])

	#adding and removing tag labels

	def add_tag_label_at_index(self,label):
		print self.selected_line_widget
		self.label_widgets[self.selected_line_widget-1].text = label


	def add_tag_label(self, label):
		self.label_widgets.append(ScrollableLabel(text = label, color = [1,1,1,1]))
		self.label_widgets[-1].ids.text_contents.halign = "center"
		self.layout.ids.taglines.add_widget(self.label_widgets[-1])

	def add_tag_labels_num_lines_screen(self):
		for num in range(self.current_index, self.current_index+self.num_lines_screen):
			self.add_tag_label(self.labels[num])


	#functions for tagging text

	def select_lineno(self, linekey):
		print self.selected_line_widget
		print len(self.line_widgets)
		if int(linekey) <= len(self.line_widgets):
			if self.selected_line_widget: #deselect any previously selected line
				self.line_widgets[self.selected_line_widget - 1].color = self.line_widgets[self.selected_line_widget - 1].last_color #make as last color thing

			self.selected_line_widget = int(linekey)
			self.line_widgets[self.selected_line_widget - 1].last_color = self.line_widgets[self.selected_line_widget - 1].color
			self.line_widgets[self.selected_line_widget - 1].color = self.color_selected

	def tag_line(self, tagkey):
		try:
			print self.tag_key_pairs[tagkey]
			print self.current_index
			print self.selected_line_widget
			print self.lines[self.current_index-self.num_lines_screen+self.selected_line_widget-1]
			print self.labels[self.current_index-self.num_lines_screen+self.selected_line_widget-1]

			self.labels[self.current_index-self.num_lines_screen+self.selected_line_widget-1] = self.tag_key_pairs[tagkey]
			self.line_widgets[self.selected_line_widget-1].last_color  = self.color_labeled

			self.add_tag_label_at_index(self.tag_key_pairs[tagkey])

		except:
			return

	def update_tag_key_pairs(self):
		if self.tag_key_pairs:
			tagstring = ' '.join([key +': '+ val for key, val in self.tag_key_pairs.items()])
			self.tag_display.text = tagstring


	#navigation functions

	def jump_to_last_untagged(self):
		for index, label in enumerate(self.labels):
			if label == '':
				print index, self.current_index
				self.current_index = index
				self.remove_lines_screen()
				self.add_labels_num_lines_screen()
				self.add_tag_labels_num_lines_screen()
				return

	#menu functions


	def dismiss_popup(self):
		Window.bind(on_key_down=self._on_keyboard_down)
		self._popup.dismiss()

	def show_load(self):
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		self.loaded_path = path
		self.loaded_filename = filename
		with open(os.path.join(path, filename[0])) as stream:
			self.load_classification_csv(stream)
		self.dismiss_popup()

	def set_num_lines_screen(self, value):
		self.num_lines_screen = int(value)
		print self.num_lines_screen
		self.dismiss_popup()

	def show_lines_page_popup(self):
		content = NumberLinesPageSlider(value = self.num_lines_screen, change_max_value = self.set_num_lines_screen)
		self._popup = Popup(title="Lines per page", content = content, size_hint=(0.4,0.4))
		self._popup.open()

	def show_tag_bind(self):
		content = AddTagDialog(cancel = self.dismiss_popup, ok = self.add_tag)
		self._popup = Popup(title="Bind new tag", content = content, size_hint = (0.4,0.4))
		self._popup.open()

	def add_tag(self, keyname, tagname):
		print keyname
		print tagname
		self.tag_key_pairs[keyname] = tagname
		self.update_tag_key_pairs()
		self.dismiss_popup()

	#tag creation



	#loading tag bindings
	def show_load_bind_tag_file(self):
		content = LoadDialog(load=self.load_tags, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load Tag file", content=content, size_hint=(0.9, 0.9))
		Window.unbind(on_key_down=self._on_keyboard_down)
		self._popup.open()

	def load_tags(self, path, filename):
		with open(os.path.join(path, filename[0])) as stream:
			readin = csv.reader(stream, delimiter = '\t')
			for line in readin:
				self.add_tag(line[0], line[1])
		self.dismiss_popup()
		self.update_tag_key_pairs()

	#exporting tag bindings and saving csv
	def show_export_tag_bindings(self):
		content = SaveDialog(save=self.export_tags, cancel = self.dismiss_popup)
		self._popup = Popup(title="Export Tags to CSV", content = content, size_hint=(0.9,0.9))
		Window.unbind(on_key_down=self._on_keyboard_down)
		self._popup.open()

	def export_tags(self, path, filename):
		with open(os.path.join(path, filename), 'w') as stream:
			writeout = csv.writer(stream, delimiter='\t')
			for key in self.tag_key_pairs.keys():
				writeout.writerow([key, self.tag_key_pairs[key]])
		self.dismiss_popup()

	def show_save_as_window(self):
		content = SaveDialog(save=self.save_csv_as, cancel = self.dismiss_popup)
		self._popup = Popup(title="Save CSV As", content = content, size_hint=(0.9,0.9))
		self._popup.open()


	def save(self):
		print self.loaded_path, self.loaded_filename
		with open(os.path.join(self.loaded_path, self.loaded_filename[0]), 'w') as stream:
			writeout = csv.writer(stream, delimiter='\t')
			for pair in zip(self.lines, self.labels):
				writeout.writerow([pair[0], pair[1]])





	def build(self):
		self.layout = MainLayout(orientation = "vertical")



		
		dropdown = MainMenu(load = self.show_load, load_tags = self.show_load_bind_tag_file, jump_untagged = self.jump_to_last_untagged, change_lines_page = self.show_lines_page_popup, export_tags = self.show_export_tag_bindings, save = self.save, add_tag = self.show_tag_bind)
		mainbutton = Button(text='Menu', size_hint_x=0.2)

		mainbutton.bind(on_release=dropdown.open)

		self.tag_display = Label(text="", size_hint_x = 0.8)




		self.layout.ids.topbar.add_widget(mainbutton)
		self.layout.ids.topbar.add_widget(self.tag_display)

		self.update_tag_key_pairs()


		return self.layout

if __name__ == "__main__":
    ScrollApp().run()
