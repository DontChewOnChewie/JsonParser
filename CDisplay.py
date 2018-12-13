import time
import os
import re

class CDisplay():

    cur_functions = [] # List to hold functions for current display.

    banner="""       _  _____  ____  _   _   _____                         
      | |/ ____|/ __ \| \ | | |  __ \                        
      | | (___ | |  | |  \| | | |__) |_ _ _ __ ___  ___ _ __ 
  _   | |\___ \| |  | | . ` | |  ___/ _` | '__/ __|/ _ \ '__|
 | |__| |____) | |__| | |\  | | |  | (_| | |  \__ \  __/ |   
  \____/|_____/ \____/|_| \_| |_|   \__,_|_|  |___/\___|_|"""
    

    ''' Initialise CDisplay Object. '''
    def __init__(self, parser):
        self.parser = parser
        self.home()


    ''' Set functions for start page. '''
    def start_options(self):
        return [ self.list_attr, self.template_choice, self.regex_choice, self.key_word_choice, self.user_search, self.display_docs, exit ]


    ''' Set functions for template page. '''
    def template_options(self):
        return [ self.included_templates, self.created_templates, self.create_template, self.delete_template, self.home, exit ]


    ''' Set functions for word search page. '''
    def word_search_options(self):
        return [ self.basic_key_word_search, self.template_key_word_search, self.create_key_word_template, self.delete_key_word_template, self.home, exit ]


    ''' Set functions for regex page. '''
    def regex_options(self):
        return [ self.simple_regex, self.included_expressions, self.created_expressions, self.create_expression, self.delete_expression, self.home, exit ]


    ''' Function to handle what to do when the user inputs their choice.
        If the user inputs an invalid choice, return the user to the
        the same screen with error message.'''
    def handle_option(self):
        user_input = input("What would you like to do?") 
        try:
            if (int(user_input) > 0 and int(user_input) < len(self.cur_functions) + 1):
                self.cur_functions[int(user_input)-1]()
            else:
                self.input_screen_change(self.display, True)
        except Exception as e:
            self.input_screen_change(self.display, True)
        except KeyboardInterrupt:
            self.home()
            

    ''' Function used to change screen, not used too much in
        the program. If an error occured show an error.'''
    def input_screen_change(self, screen, error):
        if error:
            print("Please enter a valid input!")
        print("\n"*20)
        print(self.display)
        self.handle_option()


    ''' Function to list all the attributes of the JSON file that
        can be searched and referenced. The for loops check for
        dictionaries inside other dictionaries and print it out
        in a readable output.'''
    def list_attr(self):
        cur_print = 0 # Variable to control printing
        
        print("\n\n\nAvailable Options to Search\n\n\n")
        cur_print = cur_print + 1
        for key in self.parser.parsed_files[0].keys():
            if 'dict' in str(type(self.parser.parsed_files[0][str(key)])):
                print("-"*20 + "\n" + key + ":")
                cur_print = cur_print + 1
                final_str = ""
                for sub_key in self.parser.parsed_files[0][str(key)].keys():
                    if not sub_key[0] == '_':
                        final_str = final_str + sub_key + ","
                print(final_str + "\n" + "-"*20)
                
                cur_print = cur_print + 1
                # If user types quit return to previous page
                if self.parser.check_stop(cur_print, 5):
                    break
            else:
                print(key)
                
                cur_print = cur_print + 1
                # If user types quit return to previous page
                if self.parser.check_stop(cur_print, 5):
                    break
        try:        
            input("Press Enter to Continue > ") # Stop from auto reseting to home screen       
        except KeyboardInterrupt:
            self.home()
            
        self.home()
        self.handle_option()

########## Template Code ##########

    ''' Function to show the user template options. The basic parameter
        is set to false by other functions that need to choose a template
        and doesn't need all the options.'''
    def template_choice(self, basic=True):
        if basic == True:
            self.display = self.get_screen(["Included Templates", "Created Templates", "Create New Template", "Delete Template", "Home", "Quit"])
            self.cur_functions = self.template_options() # Set functions.
            print("\n"*20)
            print(self.display)
            self.handle_option()
        else:
            self.display = self.get_screen(["Included Templates", "Created Templates"])
            print("\n"*20)
            print(self.display)
            choice = 0

            # Make sure user inputs a valid option.
            while choice < 1 or choice > 2:
                try: 
                    choice = int(input("INVALID INPUT (" + str(choice) + ")! - Use an Included Template or a Created Template : "))
                except Exception as e:
                    print(e)
                except KeyboardInterrupt:
                    self.home()

            # Return users choice.
            if choice == 1:
                return "included"
            else:
                return "user"


    ''' Function to show the user what included templates the user
        can choose to use. basic is again used to differentiate
        between other functions calling it to choose a specific template.'''
    def included_templates(self, basic=True):
        self.display = self.get_screen(self.load_file_display("I", "templates"))
        self.tmpl_type = "included"
        print("\n"*20)
        print(self.display)

        if not basic:
            return self.get_file(t=False)
        else:
            self.get_file()


    ''' Function to show the user what created templates the user can
        choose to use. basic is the same as in included_templates() and
        template_choice().'''
    def created_templates(self, basic=True):
        self.display = self.get_screen(self.load_file_display("C", "templates"))
        self.tmpl_type = "user"
        print("\n"*20)
        print(self.display)

        if not basic:
            return self.get_file(t=False)
        else:
            self.get_file()


    ''' Function called when the user wants to create a new .tmpl file.'''
    def create_template(self):   
        self.parser.write_to_file("templates/user/", "tmpl")
        # Go back to template choice screen after file has been created.
        self.template_choice()


    ''' Function called when a users wants to delete a .tmpl file. '''
    def delete_template(self):
        self.display = self.get_screen(self.load_file_display("C", "templates"))
        print("\n"*20)
        print(self.display)
        self.parser.delete_file("templates/user/")
        self.template_choice()


    ''' Function to get the file the user chose based on their input.
        The t value is the same as basic in the previous functions. This
        function also decides how many records should be outputted as well
        as outputting the records.'''
    def get_file(self, t=True):
        try:
            file = input("Choose Template to use : ")
            # If user selects the back option go back to previous screen.
            if int(file) == len(os.listdir("templates/" + self.tmpl_type)) + 1:
                self.template_choice()
                return

            # Regex to find the file the user chose.
            m = re.findall(str(file) + '\. (.*?\.tmpl)' , self.display)

            # If the function has been called by either a word or regex
            # function return the file to be used.
            if not t:
                return str(m[0])
                            
            records = input("How many records should be displayed? (* = all): ")
            print("\n"*5)
            self.parser.read_template("templates\\" + self.tmpl_type + "\\" + m[0], count=records)
            self.home()
        except Exception as e:
            print("Invalid Input, Please enter an exiting option.")
            if(self.tmpl_type == "user"):
                self.created_templates()
            elif(self.tmpl_type == "included"):
                self.included_templates()
        except KeyboardInterrupt as ke:
            self.home()

########## End of Template Code ##########
                
            
########## Key Word Search Code ##########

    ''' Function used to show the user what options are available for
        the key_word section of the program. '''
    def key_word_choice(self):
        self.display = self.get_screen(["Simple Word Search", "Template Word Search", "Create New Template Word Search", "Delete Template Word Search", "Home", "Quit"])
        self.cur_functions = self.word_search_options()
        print("\n"*20)
        print(self.display)
        self.handle_option()
    

    ''' Function used to perform single word searches. The user
        has to enter a value between 1 and 3 based on what field
        they want to search and then prints out the values based
        on this input.'''
    def basic_key_word_search(self):
        word = input("What word would you like to search for? : ")
        print("1. Tweet Text\n2.Username\n3.Location")

        # Try used to make sure the user inputs a number not a string.
        try:
            search_type = int(input("What field should be searched? : "))
            # Make sure the user inputs a valid value.
            while search_type < 1 or search_type > 3:
                print("Please enter a number between 1 and 3.")
                search_type = int(input("What field should be searched? : "))
        except KeyboardInterrupt:
            self.home()
        except:
            print("Please enter a number between 1 and 3.")
            self.basic_key_word_search()

        template = self.get_template() # Get template file.

        # Get parser to do the word search.
        self.parser.search_word(word, search_type, template)
        self.home()


    ''' Function used to get the users choice for a Word Template,
        also calls the functions to display the results of the users
        choice.'''
    def template_key_word_search(self):
        # Get all available Word Template choices.
        vals = self.get_key_word_template_values()
        print("\n"*20)
        print(self.display)

        # Try used to make sure the user inputs a number and not a string.
        try:
            choice = int(input("Choose a Template Word to Use : "))
            # Make sure the user inputs a valid value.
            while choice < 1 or choice > vals:
                choice = int(input("Choose a Template Word to Use : "))
            category = self.get_key_word_template(choice)
            template = self.get_template() # Get template file.
            self.parser.parse_word_template_file(category, template)
            self.home()
        except KeyboardInterrupt:
            self.home()
        except:
            print("Please enter a valid number.")
            self.template_key_word_search()


    ''' Function used to parse the users input and find locate
        the correct Word Template file to use.'''
    def get_key_word_template(self, choice):
        # Regex used to find the users choice within the display.
        val = re.findall(str(choice) + ".*", self.display)[0].split('.')[1].lstrip().rstrip()

        # If the users has chose to go back, retrun them to the previous screen.
        if val == "Back":
            self.key_word_choice()
            return
        return val


    ''' Function used to create a new Word Template '''
    def create_key_word_template(self):
        self.parser.add_word_template()
        self.key_word_choice()


    ''' Function used to delete a key word template of the users choice. '''
    def delete_key_word_template(self):
        self.get_key_word_template_values()
        print("\n"*20)
        print(self.display)
        self.parser.delete_word_template(self.display)
        self.key_word_choice()


    ''' Function used to get the available Word Template options
        that the user can pick from and set the display to show them.'''
    def get_key_word_template_values(self):
        vals = []
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                vals.append(line.split("^")[0].rstrip().lstrip())
        vals.append("Back")
        self.display = self.get_screen(vals)
        return len(vals)
        
 


########## End of Key Word Search Code ##########


########## Regex Search Code ##########


    ''' Function used to show the user the available options in the
        regex part of the program. '''
    def regex_choice(self):             
        self.display = self.get_screen(["Simple Regex Expression", "Included Expression", "Created Expression", "Create New Expression", "Delete Expression", "Home", "Quit"])
        self.cur_functions = self.regex_options()
        print("\n"*20)
        print(self.display)
        self.handle_option()


    ''' Function used to get a regular expression from the user and pass
        that expression to the relevant functions in JsonParser.py. '''
    def simple_regex(self):
        try:
            expression = input("What Expression should be Used? : ")
        except KeyboardInterrupt:
            self.home()
        
        # Choose Template for Regex Search
        template = self.get_template()
        
        self.parser.simple_regex_search(expression, template)
        self.home()


    ''' Function used to show the user what included regular expressions (.expr)
        they can use to search the tweet data.'''
    def included_expressions(self):
        self.display = self.get_screen(self.load_file_display("I", "expressions"))
        self.expr_type = "included"
        print("\n"*20)
        print(self.display)
        self.get_expressions_file()


    ''' Function used to show the user what created regular expression (.expr)
        they can use to search the tweet data. '''
    def created_expressions(self):
        self.display = self.get_screen(self.load_file_display("C", "expressions"))
        self.expr_type = "user"
        print("\n"*20)
        print(self.display)
        self.get_expressions_file()


    ''' Function used to create a new .expr file. '''
    def create_expression(self):   
        self.parser.write_to_file("expressions/user/", "expr")
        self.regex_choice()


    ''' Function used to delete a specified created .expr file.'''
    def delete_expression(self):
        self.display = self.get_screen(self.load_file_display("C", "expressions"))
        print("\n"*20)
        print(self.display)
        self.parser.delete_file("expressions/user/")
        self.regex_choice()

    ''' Function used to get the expression file specified by the user
        and calling functions within the JsonParser.py file to display
        the results of the search.'''
    def get_expressions_file(self):
        try:
            file = input("Choose Expression to use : ")
            # User has selected back.
            if int(file) == len(os.listdir("expressions/" + self.expr_type)) + 1:
                self.regex_choice()
                return

            # Regular expression to find the correct file to use.       
            m = re.findall(str(file) + '\. (.*?\.expr)' , self.display)
                    
            # Choose Template for Regex Search
            template = self.get_template()
                                    
            self.parser.read_expression("expressions/" + self.expr_type + "/" + m[0].lstrip().rstrip(), template)
            self.home()
        except Exception as e:
            print(e)
            print("Invalid Input, Please enter an exiting option.")
            if(self.expr_type == "user"):
                self.created_expressions()
            elif(self.expr_type == "included"):
                self.included_expressions()
        except KeyboardInterrupt:
            self.home()

########## End of Regex Search Code ##########


########## User Search Code ##########

    ''' Function used to call a user search in JsonParser.py. '''
    def user_search(self):
        try:
            user = input("Name of User : ")
            self.parser.user_search(user)
            self.home()
        except KeyboardInterrupt:
            self.home()

########## End of User Search Code ##########

    ''' Function used to show the user the home page of the program.
        This function is used throughout the code.'''           
    def home(self):
        self.display = self.get_screen(["Show All Attributes", "Template Display", "RegEx Search", "Key Word Search", "User Search", "Documentation", "Exit"])
        self.cur_functions = self.start_options()
        print("\n"*20)
        print(self.display)
        self.handle_option()


    ''' Function used to display the documentation for the program to the user. '''
    def display_docs(self):
        try:
            with open("documentation.txt", 'r') as file:
                print(self.banner)
                for line in file:
                    print(line)
            input("Press Enter to Continue > ") # Stop immediate return to home.
            self.home()
        except:
            print("Documentation file missing, re-install or look online for help.")
            try:
                input("Press Enter to Continue > ") # Stop immediate return to home.
                self.home()
            except KeyboardInterrupt:
                self.home()
            

    ''' This function is one of the most important function in the program,
        options is the values to be displayed on the screen for the current choice.
        Basically this function determines what is displayed on screen to the user. '''
    def get_screen(self, options):
        screen = self.banner + "\n\n"
        for i in range(0,len(options)):
            screen = screen + str(i+1) + ". " + options[i] + "\n"
        screen = screen + "\nCreated by Oliver Bowker (Bowker Productions)"
        return screen

## Cross Type Functions ##

    ''' Function used to get a template (.tmpl) file to use for both
        word search and regex search functions.'''
    def get_template(self):
        template_path = ""
        template_type = self.template_choice(basic=False)
        template_path = "templates/" + template_type

        template_name = "Back"
        while template_name == "Back":
            if template_type == "included":
                template_name = self.included_templates(basic=False)
            else:
                template_name = self.created_templates(basic=False)
        template_path = template_path + "/" + template_name
        return template_path


    ''' Function used to get file display for both expression files and
        template files dependant on if the user wants to see included files
        or user created files. '''
    def load_file_display(self, choice, fileType): 
        if (choice == "I"):
            ret = os.listdir(fileType+"/included")
            ret.append("Back")
            return ret
        if (choice == "C"):
            ret = os.listdir(fileType + "/user")
            ret.append("Back")
            return ret







        
