import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.uix.popup import Popup
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import os
import webbrowser
import folium
from folium.plugins import HeatMap
import JsonParser as jp
import graphs as g

# Multi Use Objects -------------------


''' Class used so the user can choose files.'''
class TemplateBrowser(Popup):

    ''' Initialise object, field refers to TextInput to files path will
        be inserted into, path is the start path, and file expected is the
        expected extension of the file the user should choose. '''
    def __init__(self, field, path, file_expected):
        super(TemplateBrowser, self).__init__()
        self.path = path
        self.field = field
        self.file_expected = file_expected
        
    ''' Function to validate the users file choice. Path passed from .kv file
        and refers to the users choice of file.'''
    def set_field(self, path):
        # Check if the user has chose a file.
        if len(path) > 0:
            # Make sure the user has selected the correct file type.
            if path[0].endswith(self.file_expected):
                if self.file_expected == ".tmpl":
                    # Cut the full path down for easier reading.
                    file = path[0].split('\\')[len(path[0].split('\\')) - 3]
                    file += "\\" + path[0].split('\\')[len(path[0].split('\\')) - 2]
                    file += "\\" + path[0].split('\\')[len(path[0].split('\\')) - 1]
                    self.field.text = file
                else:
                    # Change field to represent success.
                    self.field.text = path[0]
                    self.field.background_color = (0.96, 0.95, 0.73, 1)
            else:
                # Change field to represent an error.
                self.field.text = "Not expected file type!"
                self.field.background_color = (0.93, 0.42, 0.35, 1)
                self.field.select_all()


''' Class used to confirm deletion of a file. '''
class ConfirmationPopup(Popup):

    ''' Initialise Object, file_name refers to the name of the file, file type is
        the type of file to be deleted, template list is the list of files that will
        need updating on deletion of a file and display is used to display if an error
        occurs.'''
    def __init__(self, file_name, file_type, template_list, display):
        super(ConfirmationPopup, self).__init__()
        self.file_name = file_name
        self.file_type = file_type
        self.display = display
        self.template_list = template_list
        self.title = "Are you sure you want to delete " + self.file_type + " '" + self.file_name + "'?"


    ''' Function used to delete file, called within the .kv file. Function handles
        the deletion of both Word Template Searches and Expression files.'''   
    def delete_file(self):    
        if self.file_type == "Word Template":
            app.parser.edit_word_template(self.file_name, "Delete")
            self.template_list.adapter.data = app.parser.get_key_word_template_values()
        elif self.file_type == "Expression File" or self.file_type == "Template File":
            app.parser.delete_file(self.file_name, self.display)
            # Make sure that template_list exists, if it does update the list.
            if self.template_list != None:
                self.template_list.adapter.data = app.parser.get_expression_files()


''' Class used to edit files including Word Templates, Template files (.tmpl)
    and Expression files (.expr). '''
class FileEditorPopup(Popup):

    # Refers to TextInput that holds the file name in the .kv file.
    file_name_input = ObjectProperty()
    # Refers to the TextInput that hold the contents of the currently loaded files.
    file_contents = ObjectProperty()


    ''' Intialise Object, edit_type refers to whether the user is creating or editing a
        file, file_name refers to the name of the current file, file_type is the type of file
        in the editor and template_list is the list of files to be updated if any changes are
        made or new files are created.'''
    def __init__(self, edit_type, file_name, file_type, template_list):
        super(FileEditorPopup, self).__init__()
        self.edit_type = edit_type
        self.file_type = file_type
        self.template_list = template_list
        self.formatted = False

        # If file name is specified set the TextInput text to reflect that.
        if file_name != None:
            self.file_name = file_name
            self.file_name_input.text = file_name

        # Set title dependant on the edit_type, get file data if editing a file.
        if self.edit_type == "Create":
            self.title = "Create New " + self.file_type
        else:
            self.title = "Editing " + self.file_type + " '" + file_name + "'"
            self.formatted = True
            self.get_file_data()


    ''' Funciton used to get file data if the user is editing a file. '''
    def get_file_data(self):
        if self.file_type == "Word Template":
            self.file_contents.text = app.parser.parse_word_template_file(self.file_name, None, search=False)
        else:
            if os.path.lexists(self.file_name):
                with open(self.file_name, 'r') as file:
                    for line in file:
                        self.file_contents.text += line
            else:
                # Change styling of inputs to reflect an error.
                self.file_name_input.text = "File Chosen Did not Exist!"
                self.file_name_input.background_color = (0.93, 0.42, 0.35, 1)


    ''' Function used to add formatting for the user when a file is created. Called in the .kv
        when the user presses the enter key in the name TextInput. '''
    def add_formatting(self, name):
        if not self.formatted and self.edit_type == "Create":
            if self.file_type == "Word Template":
                self.file_contents.text = name + " ^ [word1, word2, word3..]"
                self.formatted = True
            elif self.file_type == "Expression File":
                self.file_contents.text = "{field_to_search} ^ expression here\
                                        \nEXCEPT ^ {field_to_except_from } excep1; {} excep2;\
                                        \nINCLUDE ^ RESULT; EXPRESSION; COUNTER;\
                                        \n\nREMOVE THIS LINE : IF YOU ARE UNSURE HOW TO WRITE AN .expr FILE CHECK OUT THE EXAMPLE OR DOCS."
                self.formatted = True


    ''' Function used to save changes to a specified file type. The clas simply calls update methods within
        the JsonParser.py file that updates or creates the file dependant on the classes edit_type.'''
    def save_changes(self):
        # Make sure the user has actually specified a file name.
        if self.file_name_input.text == "":
            self.file_name_input.hint_text = "Specify Name of File"
            self.file_name_input.background_color = (0.93, 0.42, 0.35, 1)
            return
        
        # Redirect if not word template
        if self.file_type == "Expression File":
            if self.edit_type == "Create":
                if app.parser.update_file(self.file_name_input.text + ".expr", self.edit_type, self.file_name_input, self.file_contents.text):
                    self.template_list.adapter.data = app.parser.get_expression_files()
                    self.dismiss()
            elif self.edit_type == "Edit":
                if app.parser.update_file(self.file_name_input.text, self.edit_type, self.file_name_input, self.file_contents.text):
                    self.template_list.adapter.data = app.parser.get_expression_files()
                    self.dismiss()
            return

        # Redirect if not word template
        if self.file_type == "Template File":
            if self.edit_type == "Create":
                if app.parser.update_file(self.file_name_input.text + ".tmpl", self.edit_type, self.file_name_input, self.file_contents.text):
                    self.dismiss()
            elif self.edit_type == "Edit":
                if app.parser.update_file(self.file_name_input.text, self.edit_type, self.file_name_input, self.file_contents.text):
                    self.dismiss()
            return
        
        if self.edit_type == "Edit":
            if self.file_type == "Word Template":
                app.parser.edit_word_template(self.file_name, "Edit", updates=self.file_contents.text)
                self.dismiss()
        else:
            if self.file_type == "Word Template":
                if app.parser.add_word_template(self.file_name_input.text, self.file_name_input, self.file_contents.text):
                    self.dismiss()
                else:
                    self.file_contents.text = ""
                    self.formatted = False
        self.template_list.adapter.data = app.parser.get_key_word_template_values()


    ''' Function used to check the validty of a given file. Called in .kv
        file when user wants to try and add formatting to a new file. If the
        name is already taken then widgets are styled to show an error.'''
    def check_file_validty(self, name):
        if name == "":
            self.file_name_input.text = "Not Valid File Name"
            self.file_name_input.background_color = (0.93, 0.42, 0.35, 1)
            return
        if self.file_type == "Word Template":
            for item in self.template_list.adapter.selection:
                if name == item.text:
                    self.file_name_input.text = "Not Valid File Name"
                    self.file_name_input.background_color = (0.93, 0.42, 0.35, 1)
                    self.file_name_input.select_all()
                    return
            self.add_formatting(name)
        elif self.file_type == "Expression File":
            if not app.parser.check_file_exists(name + ".expr"):
                self.add_formatting(name)
            else:
                self.file_name_input.text = "Shared File Name"
                self.file_name_input.background_color = (0.93, 0.42, 0.35, 1)
                self.file_name_input.select_all()
                return

    ''' Function used to open up an ExamplePopup in order to show the user an
        example of the file structure to use for the given file being created.'''              
    def show_example(self):
        if self.file_type == "Word Template":
            popup = ExamplePopup("Template Name ^ [Comma Seperated Values]", self.file_type)
            popup.open()
        elif self.file_type == "Expression File":
            popup = ExamplePopup("{Field To Search In} ^ Expression to be done on field\
                                 \nEXCEPT ^ {field_to_check_against} ItemToIgnore1; {} ItemToIgnore2;\
                                 \nINCLUDE ^ RESULT; EXPRESSION; COUNTER;\
                                 \n\nExpression files can be extremely powerful however are easy to code wrong.\
                                 \nExample\
                                 \nLine 1 : {text} ^ Sue|John\
                                 \nLine 2 : EXCEPT ^ {user:name} Henry123; {user:name} Joe345;\
                                 \nLine 3 : INCLUDE ^ RESULT; COUNTER;\
                                 \n\nThe example above would search for tweet texts with the name Sue or John in, except if those tweets were from either user Henry123 or Joe345.\
                                 \nThe INCLUDE statement can only have 3 values, RESULT (what the regualr expression found), EXPRESSION (the expression used) and COUNTER (the record number currently displayed).\
                                 \nNOTE! : Pay attenion to the syntax, especially how ;, ^, : and {} are used throughout.", self.file_type)
            popup.open()
        elif self.file_type == "Template File":
            popup = ExamplePopup("{Field to Search} any kind of formatting can be used around this file.\
                                \n\nExample:\
                                \nUsername : {user^name}, Screen Name : {user^screeName}\
                                \nTweet Content : {text}\
                                \n\nThe information between {} refers to dictionary values, the ^ indicates a sub dictionary. Anything other than the {} can be used to format data however the user wants.", self.file_type)
            popup.open()


''' Class used to show an example file and simple documentation of the
    file type they are editing or creating.'''    
class ExamplePopup(Popup):
    example_box = ObjectProperty() # Where the example file data is displayed.

    ''' Initialise Object, example is the text to show for the example and title
        is the title of the popup.'''
    def __init__(self, example, title):
        super(ExamplePopup, self).__init__()
        self.example_box.text = example
        self.title = title + " Example"


''' Class used to get confirmation to continue from the user when there are
    potentially too many markers put onto a folium map.'''
class MarkerPopup(Popup):
    def open_map(self):
        MapPopup().open()

''' Class used show the small window where users can choose to edit .tmpl files.'''
class TemplateEditorPopup(Popup):
    # Refers to the path of the file or the name of the new file
    # the user wants to edit/create
    file_path = ObjectProperty()

    ''' Function that opens a template/file browser. '''
    def open_file_dialog(self):
        popup = TemplateBrowser(self.file_path, 'templates/', '.tmpl')
        popup.open()


    ''' Function that opens a confirmation popup when a file has been selected
        to be deleted.'''
    def open_confirm(self):
        if app.parser.check_file_exists(os.path.basename(self.file_path.text)):
            popup = ConfirmationPopup("templates/user/" + os.path.basename(self.file_path.text), 'Template File', None, self.file_path)
            popup.open()
        else:
            # Inputted file does not exists, show error style/message
            self.file_path.text = "File Does not Exist"
            self.file_path.background_color = (0.93, 0.42, 0.35, 1)

    ''' Function to open a new file editor. '''
    def open_file_editor(self, edit_type):
        if edit_type == "Edit":
            # Make sure that the file is editable.
            if not os.path.lexists(self.file_path.text) or not self.file_path.text.endswith(".tmpl"):
                self.file_path.text = "Not a valid .tmpl file"
                self.file_path.background_color = (0.93, 0.42, 0.35, 1)
                return
            
        popup = FileEditorPopup(edit_type, self.file_path.text, "Template File", None)
        popup.open()


''' Class used display different graphs. '''
class GraphPopup(Popup):
    # Controls which graph to display.
    counter = 0
    # Layout to where the graph will be added.
    add_to = ObjectProperty()

    ''' Intialise Object, parser is the current parser, user for
        accessing results from a search.'''
    def __init__(self, parser):
        super(GraphPopup, self).__init__() 
        self.parser = parser
        self.grapher = g.Graphs(self.parser)
        self.title = "Pie Chart to show Sensitive vs Non-Sensitive Tweets"
        self.change_graph(0)

    ''' Function used to clear a graph from the screen so a new graph
        can be added to the screen.'''
    def clear_graph(self):
        for child in self.add_to.children:
            if 'garden' in str(type(child)):
                self.add_to.remove_widget(child)

    ''' Function used to change the to a different graph. '''
    def change_graph(self, increment):
        self.counter += increment
        if self.counter > 2:
            self.counter = 0
        elif self.counter < 0:
            self.counter = 2

        title_mod = ""
        if len(app.parser.results) > 250:
            title_mod = " : Too many records to create Most Used Words Bar (" + str(len(app.parser.results))+ ")"

        self.clear_graph()
        if self.counter == 0:
            self.title = "Pie Chart to show Sensitive vs Non-Sensitive Tweets" + title_mod
            self.add_to.add_widget(self.grapher.sensitive_tweets_pie())
        elif self.counter == 1:
            self.title = "Line Chart to show Number of Tweets Made per Day" + title_mod
            self.add_to.add_widget(self.grapher.date_based_line())
        elif self.counter == 2:
            # Porgram will halt if too many records needs to be searched.
            if len(app.parser.results) < 250:
                self.title = "Bar Chart to show Most Used Words"
                self.add_to.add_widget(self.grapher.most_used_words_bar())
            else:
                # Reset graph counter
                if increment == -1:
                    self.counter = 1
                else:
                    self.counter = 0
                self.change_graph(0)
                
''' Class used to display correct graph. '''       
class MapPopup(Popup):

    ''' Function used to open the type of map the user specifies.'''
    def open_map(self, map_type):
        if map_type == "Marker":
            webbrowser.open('file://' + os.path.realpath("mapping.html"))
        elif map_type == "Heat":
            webbrowser.open('file://' + os.path.realpath("heat_map.html"))
    
# Screen Objects -------------------

''' This class is the screen that the user first sees when the program starts. '''
class StartScreen(Screen):

    # Layout with all the TextInputs.
    inputs = ObjectProperty()
    # Label that relays messages to the user.
    status_label = ObjectProperty()
    # Button that controls whether the user has
    # successfully parsed files.
    view_data_btn = ObjectProperty()


    ''' Function used to open a Template/File browser. '''
    def open_file_dialog(self, btn):
        popup = TemplateBrowser(self.get_field(btn), os.getcwd(), '.json')
        popup.open()


    ''' Function used to get a specific input based on the button pressed.'''
    def get_field(self, btn):
        for item in btn.parent.children:
            if "TxtInput" in str(type(item)):
                return item

    ''' Function used to get the files/paths from the TextInputs and if the user
        successfully parses data enable the view_data_btn so the user can start
        searching through the data. '''
    def get_files(self):
        self.status_label.text = "Parsing Files"

        # Get users inputted file paths.
        self.get_inputs()

        # If the user has parsed a valid file, allow continiung to main page
        if app.parser.files_parsed:
            self.view_data_btn.background_color = (0, 0.69, 0.3, 1)
            self.view_data_btn.text = "->"
            self.view_data_btn.active = True
        else:
            self.view_data_btn.background_color = (0.93, 0.42, 0.35, 1)
            self.view_data_btn.text = "X"
            self.view_data_btn.active = False


    ''' Function used to get all the TextInputs on the start screen so the files/paths
        can be parsed by JsonParser.py.'''
    def get_inputs(self):
        files = []
        textfields = []
        
        for child in list(self.inputs.children):
            if "InputField" in str(type(child)):    
                for c in list(child.children):
                    if "TxtInput" in str(type(c)):
                        files.append(c.text)
                        textfields.append(c)
        # Points to a function that will parse the JSON files.
        app.parser.read_files(files, textfields, self.status_label)

    ''' Function that transition to the main screen, if files have been parsed. '''   
    def view_parsed_data(self):
        if self.view_data_btn.active:
            app.root.current = 'main_screen'
        else:
            self.status_label.text = "No Valid Files have been Parsed."        

''' Template Class, widgets defined in .kv file. '''    
class JsonFileField(BoxLayout):
    pass

''' Template Class, widgets defined in .kv file. '''
class MainScreen(Screen):
    display = ObjectProperty()
    counter = 0

    def show_record(self, increment):
        if len(app.parser.results) < 1:
            app.parser.results = app.parser.parsed_files
        
        self.counter += 1
        if self.counter > len(app.parser.parsed_files) - 1:
            self.counter = 0
        elif self.counter < 0:
            self.counter = len(app.parser.parsed_files) -1

        self.display.text = app.parser.read_template("templates/included/basic.tmpl", self.counter)
        self.display.scroll_y = 0
                
    def show_docs(self):
        data = ""
        with open("documentation.txt", 'r') as file:
            for line in file:
                data += line
        self.display.text = data
        self.display.scroll_y = 0

''' Template Class, widgets defined in .kv file. '''
class TemplateButton(ListItemButton):
    pass


''' This class is the screen that the user sees when they want to do
    word searches or template searches. '''
class WordSearchScreen(Screen):
    template_path = ObjectProperty() # Path of .tmpl file to use.
    record_display = ObjectProperty() # TextInput where records are displayed.
    template_list = ObjectProperty() # List of all available Word Templates.
    
    record_counter = 0

    ''' Function to open a Template/File browser. '''
    def open_file_dialog(self):
        popup = TemplateBrowser(self.template_path, os.getcwd(), '.tmpl')
        popup.open()

    ''' Function to open a ConfirmationPopup when user wants to delete a file. '''
    def open_confirm(self, file_name, file_type):
        popup = ConfirmationPopup(file_name, file_type, self.template_list, self.record_display)
        popup.open()

    ''' Funtion used to open a file editor. '''
    def open_editor(self, edit_type, file_name, file_type):
        popup = FileEditorPopup(edit_type, file_name, file_type, self.template_list)
        popup.open()

    ''' Function used to open a GraphPopup '''
    def open_graphs(self):
        if len(app.parser.results) < 1:
            return
        
        popup = GraphPopup(app.parser)
        popup.open()

    ''' Function used to check that the user can search, then do the correct search type
        dependant on the users actions. '''
    def check_search(self, word, search_type):
        # Check if .tmpl file is valid.
        if self.template_path.text.endswith(".tmpl")and os.path.exists(self.template_path.text):
            if search_type == "Simple":
                app.parser.search_word(word)
            elif search_type == "Template" and len(self.template_list.adapter.selection) > 0:
                app.parser.parse_word_template_file(self.template_list.adapter.selection[0].text, self.template_path.text)
            self.show_new_record(0)
            print(str(len(app.parser.results)))
        else:
            # Incorrect .tmpl selection, show error.
            self.record_display.text = "! - File Either does not Exist, Incorrect template file type or no template has been selected. - !"
            self.template_path.background_color = (0.93, 0.42, 0.35, 1)


    ''' Function used to go through the records, increment is passed dependant on button
        pressed, this is passed mainly in the .kv file. '''
    def show_new_record(self, increment):
        # Check there are results to cycle through.
        if len(app.parser.results) > 0 and os.path.exists(self.template_path.text):
            self.record_counter += increment

            # Stop IndexOutOfBoundsException
            if self.record_counter > len(app.parser.results)-1:
                self.record_counter = 0
            if self.record_counter < 0:
                self.record_counter = len(app.parser.results)-1
                
            self.record_display.text = app.parser.read_template(self.template_path.text, self.record_counter)
        else:
            self.record_display.text = "! - Template does not Exist or no Records have been Parsed - !"


    ''' Function called in .kv file dependant on if the user wants to create or
        edit a file. '''
    def template_editor(self, edit_type):
        if edit_type == "Create":
            self.open_editor(edit_type, None, "Word Template")
        else:
            # Check that a Word Template has been selected.
            if len(self.template_list.adapter.selection) > 0:
                self.open_editor(edit_type, self.template_list.adapter.selection[0].text, "Word Template")
            else:
                self.record_display.text = "! - No Template Selected for Editing - !"

    ''' Function used to delete a Word Template. '''            
    def delete_template(self):
        if len(self.template_list.adapter.selection) > 0:
            file = self.template_list.adapter.selection[0].text
            self.open_confirm(file, "Word Template")
        else:
            self.record_display.text = "! - No Template Selected For Deletion - !"
            
    ''' Function used to show map data for the current results after a search by the user.'''
    def show_mapped_data(self):
        # If no results don't map anything
        if len(app.parser.results) < 1:
            return
        
        if len(app.parser.results) > 20:
            popup = MarkerPopup()
            popup.open()
        else:
            results = []
            # Pinned Map
            map_pins = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            # HeatMap Map
            map_heat = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            for diction in app.parser.results:
                folium.Marker([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']], popup=diction['user']['name']).add_to(map_pins)
                results.append([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']]) # To be added to HeatMap
            map_pins.save("mapping.html") # Save Pin Map
            hm = folium.plugins.HeatMap(results)
            map_heat.add_child(hm)
            map_heat.save("heat_map.html") # Save HeatMap
            MapPopup().open()


''' This class is the screen that the user sees when they want to do
    regular expression searches. '''
class RegexSearchScreen(Screen):
    template_path = ObjectProperty() # Path of .tmpl file to use.
    template_list = ObjectProperty() # List of available expression files.
    record_display = ObjectProperty() # TextInput where records are displayed.

    record_counter = 0

    ''' Function used to open a Template/File browser. '''
    def open_file_dialog(self):
        popup = TemplateBrowser(self.template_path, os.getcwd(), '.tmpl')
        popup.open()
     
    ''' Function used to open a new file editor. '''
    def open_editor(self, edit_type, file_name, file_type):
        # Don't allow editing of included files
        if file_name != None:
            if "included" in file_name:
                self.record_display.text = "! - Can't Edit Included Expression - !"
                return
        
        popup = FileEditorPopup(edit_type, file_name, file_type, self.template_list)
        popup.open()

    ''' Function used to open a ConfirmationPopup when the user wants to delete a file. '''
    def open_confirm(self, file_name, file_type):
        popup = ConfirmationPopup(file_name, file_type, self.template_list, self.record_display)
        popup.open()

    ''' Function used to open a GraphsPopup. '''
    def open_graphs(self):
        if len(app.parser.results) < 1:
            return
        
        popup = GraphPopup(app.parser)
        popup.open()

    ''' Function used to check that the user can search, then do the correct search type
        dependant on the users actions. '''
    def check_search(self, expr, search_type):
        if self.template_path.text.endswith(".tmpl") and os.path.lexists(self.template_path.text):
            if search_type == "Simple":
                app.parser.simple_regex_search(expr)
            elif search_type == "Template" and len(self.template_list.adapter.selection) > 0:
                app.parser.get_expression_path(self.template_list.adapter.selection[0].text, self.record_display)
            self.show_new_record(0)
            print(str(len(app.parser.results)))
        else:
            self.record_display.text = "! - File Either does not Exist, Incorrect template file type or no template has been selected. - !"
            self.template_path.background_color = (0.93, 0.42, 0.35, 1)

    ''' Function used to go through the records, increment is passed dependant on button
        pressed, this is passed mainly in the .kv file. Slightly differnt to the same fucntion
        in the class WordSearchScreen, as extra values must be added on the end. '''             
    def show_new_record(self, increment):
        if len(app.parser.results) > 0 and os.path.lexists(self.template_path.text):
            self.record_counter += increment
            
            if self.record_counter > len(app.parser.results)-1:
                self.record_counter = 0
            if self.record_counter < 0:
                self.record_counter = len(app.parser.results)-1
                
            self.record_display.text = app.parser.read_template(self.template_path.text, self.record_counter)

            # Handle Includes in the .expr file used.
            if app.parser.expr_results != None:
                if len(app.parser.expr_results) > 0:
                    self.record_display.text += "\nResults : " + app.parser.expr_results[self.record_counter]
                if app.parser.last_expression != None:
                    self.record_display.text += "\nExpression : " + app.parser.last_expression
                if app.parser.include_counter:
                    self.record_display.text += "\nRecord Number : " + str(self.record_counter+1)
        else:
            self.record_display.text = "! - Template does not Exist or no Records have been Parsed. If a custom file has been used \
                                        make sure that it is formatted correctly. - !"


    ''' Function called in .kv file dependant on if the user wants to create or
        edit a file. '''            
    def template_editor(self, edit_type):
        if edit_type == "Create":
            self.open_editor(edit_type, None, "Expression File")
        else:
            if len(self.template_list.adapter.selection) > 0:
                self.open_editor(edit_type, app.parser.get_expression_path(self.template_list.adapter.selection[0].text, None, search=False), "Expression File")
            else:
                self.record_display.text = "! - No Template Selected for Editing - !"

    ''' Function used to delete an Expression File. ''' 
    def delete_template(self):
        if len(self.template_list.adapter.selection) > 0:
            file = self.template_list.adapter.selection[0].text
            self.open_confirm("expressions/user/" + file, "Expression File")
        else:
            self.record_display.text = "! - No Template Selected For Deletion - !"
            
    ''' Function used to show map data for the current results after a search by the user.'''                    
    def show_mapped_data(self):
        # If no results don't map anything
        if len(app.parser.results) < 1:
            return
        
        if len(app.parser.results) > 20:
            popup = MarkerPopup()
            popup.open()
        else:
            results = []
            # Pinned Map
            map_pins = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            # HeatMap Map
            map_heat = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            for diction in app.parser.results:
                folium.Marker([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']], popup=diction['user']['name']).add_to(map_pins)
                results.append([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']]) # To be added to HeatMap
            map_pins.save("mapping.html") # Save Pin Map
            hm = folium.plugins.HeatMap(results)
            map_heat.add_child(hm)
            map_heat.save("heat_map.html") # Save HeatMap
            MapPopup().open()
            

''' Class used in order to search '''
class UserSearchScreen(Screen):
    
    record_display = ObjectProperty()
    template_path = ObjectProperty()
    record_counter = 0

    ''' Function used to open a Template/File browser. '''
    def open_file_dialog(self):
        popup = TemplateBrowser(self.template_path, os.getcwd(), '.tmpl')
        popup.open()

    ''' Function used to open a GraphsPopup. '''
    def open_graphs(self):
        if len(app.parser.results) < 1:
            return
        
        popup = GraphPopup(app.parser)
        popup.open()


    ''' Function used to get users data and display it to the user.'''
    def get_user_info(self, selection):
        if os.path.lexists(self.template_path.text):
            app.parser.get_user_data(selection)
            self.record_counter = 0
            self.show_new_record(0)
        else:
            self.record_display.text = "! - No Valid Template Selected - !"
            self.template_path.background_color = (0.93, 0.42, 0.35, 1)

    ''' Function used to go through the records, increment is passed dependant on button
        pressed, this is passed mainly in the .kv file. '''
    def show_new_record(self, increment):
        self.record_counter += increment
        if self.record_counter < 0:
            self.record_counter = len(app.parser.results)
        elif self.record_counter > len(app.parser.results):
            self.record_counter = 0

        if os.path.lexists(self.template_path.text):
            # If record_counter = 0 then show user data instead of users records.
            if self.record_counter == 0:
                self.record_display.text = app.parser.user_data
            else:
                self.record_display.text = app.parser.read_template(self.template_path.text, self.record_counter -1)
        else:
            self.record_display.text = "! - No Valid Template Selected - !"
            self.template_path.background_color = (0.93, 0.42, 0.35, 1)
            
    ''' Function used to show map data for the current results after a search by the user.'''                    
    def show_mapped_data(self):
        # If no results don't map anything
        if len(app.parser.results) < 1:
            return
        
        if len(app.parser.results) > 20:
            popup = MarkerPopup()
            popup.open()
        else:
            results = []
            # Pinned Map
            map_pins = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            # HeatMap Map
            map_heat = folium.Map(location=[app.parser.results[0]['geoLocation']['latitude'], app.parser.results[0]['geoLocation']['longitude']])
            for diction in app.parser.results:
                folium.Marker([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']], popup=diction['user']['name']).add_to(map_pins)
                results.append([diction['geoLocation']['latitude'], diction['geoLocation']['longitude']]) # To be added to HeatMap
            map_pins.save("mapping.html") # Save Pin Map
            hm = folium.plugins.HeatMap(results)
            map_heat.add_child(hm)
            map_heat.save("heat_map.html") # Save HeatMap
            MapPopup().open()
        
        
''' Mostly a template class, holds all screens for the program. '''     
class MyManager(ScreenManager):

    ''' Function used to open a Template Editor for the NavBar. '''
    def open_template_editor(self):
        popup = TemplateEditorPopup()
        popup.open()
    
''' Class where the program starts, holds the parser referenced by all other
    functions '''        
class JsonParserApp(App):
    parser = jp.JsonParser()

''' Function used to create needed files for program to run. '''
def setup():
    if not os.path.isdir("templates"):
        os.mkdir("templates")
        os.mkdir("templates/included")
        os.mkdir("templates/user")

    if not os.path.isdir("expressions"):
        os.mkdir("expressions")
        os.mkdir("expressions/included")
        os.mkdir("expressions/user")

    if not os.path.isdir("wordTemplates"):
        os.mkdir("wordTemplates")
        write_files()


''' Function used to create all .expr, .tmpl and Key Word files.'''
def write_files():
    tmpl_basic = "------------------------------------------------\n\
Username : {user^name}\n\
Location : {geoLocation^latitude} , {geoLocation^longitude} City - {place^name}\n\
Tweet Text : {text}\n\
------------------------------------------------"
    tmpl_stats = "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-\n\
Username : {user^name}\n\
Location : {place^name} ||| Date : {createdAt^$date}\n\
Tweet Text : {text}\n\
Favourites : {favoriteCount} ||| Retweets : {retweetCount}\n\
-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
    tmpl_user_dump = "Username :- {user^name}\n\
Screen Name :- {user^screenName}\n\
From :- {user^location}\n\
Description :- {user^description}\n\
Account Created :- {user^createdAt^$date}\n\
Tweet Text :- {text}"
    
    expr_email = "{text} ^ [a-zA-Z0-9]+@[a-zA-Z0-9]*\.[com|gov|co\.uk|net]+"
    expr_url = "{text} ^ [http|https|www\.]+.*\.+[com|net|gov|co\.uk]+"
    expr_sensitive = "{isPossiblySensitive} ^ True\nEXCEPT ^\nINCLUDE ^  COUNTER;"
    expr_cust_example = "{text} ^ [a-zA-Z0-9]+@[a-zA-Z0-9]*\.[com|gov|co\.uk|net]+\n\
EXCEPT ^ {user:name} Education Matters; {user:name} Inspired Gymnastics;\n\
INCLUDE ^ EXPRESSION;"

    word_templates = "Crime ^ [theft, robbery, murder, assault, blackmail, criminal]\nViolence ^ [violence, stabbed, stabbing, knife attack, riot]\n\
Drugs ^ [weed, marijuana, ketamine, xanax, cocaine, spice, smack, LSD, mushrooms]"

    with open("templates/included/basic.tmpl", 'w') as file:
        file.write(tmpl_basic)
    with open("templates/included/stats.tmpl", 'w') as file:
        file.write(tmpl_stats)
    with open("templates/included/userInfo.tmpl", 'w') as file:
        file.write(tmpl_user_dump)
    with open("expressions/included/email.expr", 'w') as file:
        file.write(expr_email)
    with open("expressions/included/url.expr", 'w') as file:
        file.write(expr_url)
    with open("expressions/included/sensitive.expr", 'w') as file:
        file.write(expr_sensitive)
    with open("expressions/user/customEmail.expr", 'w') as file:
        file.write(expr_cust_example)
    with open("wordTemplates/wordTemplates.txt", 'w') as file:
        file.write(word_templates)

''' If the user is running the source file and not calling it
    through another file run the program. This is mainly just
    a convention of the language.'''

if __name__ == '__main__':
    setup()
    app = JsonParserApp()
    app.run()



