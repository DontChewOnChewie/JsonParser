import json
import os
import re

class JsonParser:

    ''' Initialise Class, intialise all arrays. '''
    def __init__(self):
        # Variable to determine whether or not any data has been got from files
        self.files_parsed = False
        self.results = []
        self.parsed_files = []
        self.users = []
        self.expr_results = None # Stop Crashing if user does simple regex search


    ''' Function responsible for reading the passed JSON files and loading them
        into an array of dictionares called parsed_files.'''
    def read_files(self, files, textfields, label):
        self.source_files = files
        self.parsed_files = []
        failed_parses = 0
        success_parses = 0
        
        for i in range(len(self.source_files)):
            # Check if file exists
            if os.path.lexists(self.source_files[i])and self.source_files[i].endswith(".json"):
                # Have to specify encoding type in order to prevent UnicodeDecodeError
                 with open(self.source_files[i], encoding='utf-8') as data:
                    for row in data:
                        data = json.loads(row)
                        self.parsed_files.append(data)
                        self.add_user(data)
                        
                # On successful file parse, show success style. 
                 textfields[i].background_color = (0,0.5,0.17,1)
                 success_parses += 1
                 self.files_parsed = True
                    
            else:
                # If file fails to parse show error style.
                if self.source_files[i] != '':
                    textfields[i].background_color = (0.93, 0.42, 0.35, 1)
                    failed_parses += 1

        # Stop user going back and parsing no files            
        if success_parses == 0:
            self.files_parsed = False
            
        label.text = "Finished Parsing : " + str(failed_parses) + " File/s Failed to Parse."       

# Template Parsing Code ------------

    ''' Funtion used to read the a .tmpl file so record is correctly diaplayed.
        files refers to .tmpl file and record is the record to be formatted
        and displayed. '''
    def read_template(self, file, record):
        contents = ""
        lines = open(file, 'r').readlines()
        
        for line in lines:
            contents = contents + self.get_line(line, self.results[record])
        return contents
            

    ''' Function responsible for parsing the data requested by user in the .tmpl file.
        Basically this function looks for the data between the {} and then uses the data
        to output the desired template layout to the screen.'''
    def get_line(self, line, diction):
        ret_str = ""
        new_val = ""
        get_val = []
        in_brackets = False
        for i in range(0, len(line)):
            if line[i] != '{' and not in_brackets:
                ret_str = ret_str + line[i]
            else:
                in_brackets = True
                if line[i] == '}':
                    in_brackets = False
                    get_val.append(new_val) # Add the last got value before searching
                    new_val = "" # Reset new_val so no overlapping
                    ret_str = ret_str + str(self.get_value(get_val, diction))
                    get_val = []
                else:
                    if line[i] == '^':
                        get_val.append(new_val)
                        new_val = ""
                    else:
                        if line[i] != "{":
                            new_val = new_val + line[i]
        return ret_str


    ''' This function simply gets the value the user has specified in the .tmpl file and returns it
        to be added to ret_str in get_line() and then contents in read_template()'''
    def get_value(self, val, diction):
        try:
            if len(val) > 1:
                return diction[val[0]][val[1]]
            elif len(val) == 1:
                return diction[val[0]]
        except:
            return "Object '" + str(val) + "' not found."


# Word Search Code ----------------- 

    ''' Function used to get the avaialble Word Templates from the file
        they are stored in. '''
    def get_key_word_template_values(self):
        vals = []
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                if line.split("^")[0].rstrip().lstrip() != "":
                    vals.append(line.split("^")[0].rstrip().lstrip())
        return vals


    ''' Function used to do a basic word search. '''
    def search_word(self, word):
        self.results = []
        for diction in self.parsed_files:
            try:
                if word in diction['text']:
                    self.results.append(diction)
            except:
                continue

    ''' Function used mainly to search a Word Template given by the user. word is
        the Key Word to use, template is the .tmpl file to use and search refers
        whether or not to do a search. '''            
    def parse_word_template_file(self, word, template, search=True):
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                if word in line:
                    try:
                        if search:
                            vals = line.split('[')[1].split(']')[0].split(',')
                            print("Vals : " + str(vals))
                            self.search_word_template(vals)
                        else:
                            return line
                    except Exception as e:
                        print(e)
                        print("Category " + word + " is not correctly formatted.")
                        

    ''' Function used to perform a Word Template search. Check if any of
        the Key Words gathered from parse_word_template_file are in the
        tweet text of any record. '''
    def search_word_template(self, key_words):
        self.results = []
        for diction in self.parsed_files:
            for word in key_words:
                if word.lstrip().rstrip() in diction['text']:
                    self.results.append(diction)


    ''' Function used to add a new word template to the file. '''
    def add_word_template(self, name, name_field, contents):
        # Check if a Word Template already exists with the same name.
        if self.check_template_exists(name.rstrip().lstrip()) or name == "":
            name_field.text = "Not Valid File Name"
            name_field.background_color = (0.93, 0.42, 0.35, 1)
            return False
        # Write new Word Template to file.
        with open("wordTemplates/wordTemplates.txt", 'a') as file:
            file.write("\n" + contents)
            return True

    ''' Function used to edit and delete Word Templates. '''            
    def edit_word_template(self, category, edit_type, updates=None):
        new_file_contents = ""
        with open("wordTemplates/wordTemplates.txt", 'r') as read_file:
            for line in read_file:
                # Remove Key Word from file if deleting. 
                if category in line and edit_type == "Delete" or line.rstrip().lstrip() == "":
                    continue
                # Edit existing Key Word file.
                elif category in line and edit_type == "Edit":
                    new_file_contents = new_file_contents + updates
                # Add any unaffected data.
                else:
                    new_file_contents = new_file_contents + line

        # Write new file contents.
        with open("wordTemplates/wordTemplates.txt", 'w') as write_file:
            write_file.write(new_file_contents)


    ''' Function used to check if a Word Template allready exists. '''                    
    def check_template_exists(self, name):
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                if name.lower() in line.lower():
                    return True
        return False

# Regex Search ------------

    ''' Function used to populate list of avaialable .expr files. '''
    def get_expression_files(self):
        files = []
        for file in os.listdir("expressions/included/"):
            files.append(file)
        for file in os.listdir("expressions/user/"):
            files.append(file)
        return files

    ''' Function used to perform a simple regular expression search. '''
    def simple_regex_search(self, expr):
        self.results = []
        for diction in self.parsed_files:
            if len(re.findall(expr, diction['text'])) > 0:
                self.results.append(diction)

    ########!!~!~~!~!~
    ########
    ##### CHECK THAT BREAK STATEMENT
    ''' Function used to get the path full path of picked expression file
        and then read the expression. display is used to display errors.
        search refers whether to do a search after, if not return the
        file path.'''                
    def get_expression_path(self, name, display, search=True):
        file_name = ""
        # Search through both possible directories for file name.
        for file in os.listdir("expressions/included/"):
            if name == file:
                file_name = "expressions/included/" + name
        for file in os.listdir("expressions/user/"):
            if file_name != "":
                break
            if name == file:
                file_name = "expressions/user/" + name
        
        if search:
            self.read_expression(file_name, display)
        else:
            return file_name


    ''' This function reads a .expr file, parsing the expression to be used,
        the EXCEPTS and the INCLUDES.'''            
    def read_expression(self, file, display):
        try:
            expr_file = open(file, 'r').readlines()
            search_location = re.findall(r'\{(.*?)\}', expr_file[0])[0]
            
            # Try to make sure that expression line is correctly formatted
            try:
                expression = expr_file[0][expr_file[0].index('^', 0, len(expr_file[0]))+1:].rstrip().lstrip()
            except:
                display.text = "Expression File " + file + " does not have correct formatting for Expression Line"
                return
            
            exceptions = None
            includes = None
            # Get EXCEPTs in file
            if len(expr_file) > 1:
                if expr_file[1].startswith("EXCEPT"):
                    exceptions = self.get_regex_excep(expr_file[1])
                elif expr_file[1].startswith("PASS"):
                    pass
                else:
                    display.text += "\nInvalid Syntax in EXCEPT Line."

            # Get INCLUDES in file.   
            if len(expr_file) > 2:
                if expr_file[2].startswith("INCLUDE"):
                    includes = self.get_regex_includes(expr_file[2])
                else:
                    display.text += "\nInvalid Syntax in INCLUDE Line."
            
            self.regex_search(expression, search_location, exceptions, includes, display)
        except:
            pass


    ''' Function responsible for parsing the EXCEPTS of a .expr file. Two arrays are returned
        one stating the field the EXCEPT is targeting, e.g. username, and the other the value
        that the should be EXCEPTED related to the field, e.g. Bob Smith.'''        
    def get_regex_excep(self, line):
        fields = [] # Fields to check
        values = [] # Values to check

        # Each EXCEPT ends with a ';' hence the for loop and split statement.
        for item in line.split(';'):
            # Regular expression to parse data between {}.
            field = re.findall(r'\{(.*?)\}', item)

            # Try used to stop empty string errors.
            try:
                value = item[item.index('}', 0, len(item))+1:].rstrip().lstrip()
            except:
                pass
    
            # If file has correct formatting add exception.
            if len(field) > 0 and len(value) > 0:
                fields.append(field[0])
                values.append(value)
        return [fields, values]


    ''' Function responsible for getting INCLUDES of a .expr file. Similar to
        EXCEPTS in struture.'''
    def get_regex_includes(self, line):
        includes = line.split('^')[1].split(';')
        
        # Remove any blank strings from array
        for i in range(len(includes)):
            if includes[i] == "":
                includes.pop(i)
            else:
                includes[i] = includes[i].lstrip().rstrip()
        if len(includes) > 0:
            return includes
        else:
            return None


    ''' Function responsible for carrying out a regex search with given .expr file
        parameters, including EXCEPTS and INCLUDES.''' 
    def regex_search(self, expr, field, exceptions, includes, display):
        self.expr_results = []
        self.last_expression = None
        self.include_counter = False
        self.results = []
        
        for diction in self.parsed_files:

            # If an error is thrown in the EXCEPT line return
            if self.check_exceptions(exceptions, diction) == "ERROR":
                return
            
            # If an EXCEPT parameter is met continue to next record
            if self.check_exceptions(exceptions, diction):
                continue

            if len(field.split(':')) == 2:
                # Search for sub dictionaries e.g. ['user']['name']
                result = re.findall(expr, str(diction[field.split(':')[0]][field.split(':')[1]]))
            else:
                result = re.findall(expr, str(diction[field]))

            # If regex finds a match print to console                    
            if len(result) > 0:
                self.results.append(diction)
        
                if includes != None:
                    if "RESULT" in includes:
                        self.expr_results.append(str(result))

                    if "EXPRESSION" in includes and self.last_expression == None:
                        self.last_expression = str(expr)

                    if "COUNTER" in includes and not self.include_counter:
                        self.include_counter = True


    ''' Function responsible for checking EXCEPTS against records. '''     
    def check_exceptions(self, exceptions, diction):
        # Return if there are no exceptions to handle
        if exceptions == None:
            return
        
        for i in range(len(exceptions[0])):
            if len(exceptions[0][i].split(":")) == 2:
                
                # Try to catch key error
                try:
                    # If field matches value of EXCEPT clause return True.
                    if diction[exceptions[0][i].split(":")[0]][exceptions[0][i].split(":")[1]] == exceptions[1][i]:
                        return True
                except:
                    return "ERROR"
                    
            else:
                # Single key matches (no sub dictionaries) search.
                if diction[exceptions[0][i]] == exceptions[1][i]:
                    return True
        return False
# ------------------------------------------


# User Search -----------------

    ''' Function used to add user to users array. Called at the start
        of the program. '''
    def add_user(self, diction):
        if diction['user']['name'] not in self.users:
            self.users.append(diction['user']['name'])

    ''' Function used to get users that match the users search. For
        example if the user searches 'ad' then all users with a user
        name that start with 'ad' will be displayed to the user. '''
    def get_users(self, search):
        # If user searches for nothing, show nothing.
        if search.rstrip().lstrip() == "":
            return []

        ret_arr = []
        for user in self.users:
            if user.startswith(search):
                ret_arr.append(user)

        # Alphatbetically sort users.
        return sorted(ret_arr, key=str.lower)


    ''' Function used to get user data to display to the user. The
        function gets the date the user joined, number of tweets, number
        of sensitive tweets, number of followers, users location, users
        screen name and the description of their profile.'''
    def get_user_data(self, selection):
        if len(selection) < 1:
            return
        
        date_joined = ""
        num_of_tweets = 0
        num_of_sensitive_tweets = 0
        followers = 0
        location = ""
        screenName = ""
        desc = ""

        # Reset results array so no old data is present.
        self.results = []
        self.user_data = ""
        for diction in self.parsed_files:
            if diction['user']['name'].lower() == selection[0].text.lower():
                try:
                    # Add users tweet to results.
                    self.results.append(diction)
                    num_of_tweets += 1
                    if diction['isPossiblySensitive']:
                        num_of_sensitive_tweets += 1
                    date_joined = str(diction['user']['createdAt']['$date'])
                    followers = diction['user']['followersCount']
                    try:
                        location = diction['user']['location']
                    except:
                        location = "No Location Found"
                    screenName = diction['user']['screenName']
                    try:
                        desc = diction['user']['description']
                    except:
                        desc = "No Description Found"
                except:
                    self.user_data = "Unable to get data on user '" + selection[0].text
                    return

        # Set data to be displayed to the user as a accessible variable in the class.
        self.user_data = "Name/ScreenName : " + selection[0].text + "/" + screenName +\
                         "\nDescription : " + desc + "\nFrom : " + location +\
                         "\nNumber of Tweets : " + str(num_of_tweets) +\
                         "\nNumber of Sensitive Tweets : " + str(num_of_sensitive_tweets) +\
                         "\nFollowers : " + str(followers)


# -------------------------------------------------------

    ''' Function to delete a file. '''
    def delete_file(self, file, display):
        # If file doesn't exist, show error.
        if not os.path.lexists(file):
            display.text = "! - File is either an Included file or does not exists -!"
            return
        else:
            os.remove(file)

    ###
    ### Add Confirmation to overwrite file?
    ###

    ''' Function used to update or create a new .tmpl or .expr file. '''
    def update_file(self, file_name, edit_type, file_field, text):
        # If file name is empty, show error.
        if os.path.basename(file_name).lstrip().rstrip() == "":
            file_field.text = "Please Enter a File Name"
            file_field.background_color = (0.93, 0.42, 0.35, 1)
            return False
    
        if edit_type == "Create":
            if not self.check_file_exists(os.path.basename(file_name)):
                if file_name.endswith(".expr"):
                    with open("expressions/user/" + file_name, 'w') as file:
                        file.write(text)
                    return True
                elif file_name.endswith(".tmpl"):
                    with open("templates/user/" + file_name, 'w') as file:
                        file.write(text)
                    return True
            else:
                # If file name exists, show error.
                file_field.text = "File Name Taken"
                file_field.background_color = (0.93, 0.42, 0.35, 1)
                return False

        ##### CHECK THIS WORKS, POTENTIAL CLASH OF NAMES.
        elif edit_type == "Edit":
            if os.path.basename(file_name) in os.listdir("expressions/user/"):
                with open(file_name, 'w') as file:
                    file.write(text)
                return True
            elif os.path.basename(file_name) in os.listdir("templates/user/"):
                with open(file_name, 'w') as file:
                    file.write(text)
                return True
            else:
                file_field.text = "Name of File Changed, Please Exit Editor!"
                file_field.background_color = (0.93, 0.42, 0.35, 1)
                return False
            return False

    ''' Function used to check if a file allready exists, if it does
        return True else return False.'''
    def check_file_exists(self, name):
        # Check .expr files.
        if name.endswith(".expr"):
            for file in os.listdir("expressions/included/"):
                if file == name:
                    return True
            for file in os.listdir("expressions/user/"):
                if file == name:
                    return True
            return False

        # Check .tmpl file.
        elif name.endswith(".tmpl"):
            for file in os.listdir("templates/included/"):
                if file == name:
                    return True
            for file in os.listdir("templates/user/"):
                if file == name:
                    return True
            return False
        return False




        


                              
