import json
from pprint import pprint
import sys
import os
import time
import re

class JsonParser():


    ''' Constructor for Parser, Parses given files and returns an error if no valid files were given '''
    def __init__(self, files):
        self.source_files = files
        print("Parsing JSON Files....") # Status Message
        self.parsed_files = self.read_files()
        
        # Check if any records were added
        if len(self.parsed_files) == 0:
            print("The given files held no JSON parsable data, please restart and select correct files.")
            exit()


    ''' This function is responsible for parsing the JSON files. All dictionaries are added to an array
        which is then set in the constructor to be equal to self.parsed_files'''
    def read_files(self):
        ret_arr = []
        
        for file in self.source_files:
            # Check if file exists
            if os.path.lexists(file) and file.endswith(".json"):
                # Have to specify encoding type in order to prevent UnicodeDecodeError
                 with open(file, encoding='utf-8') as data:
                     for row in data:
                        data = json.loads(row)
                        ret_arr.append(data)
            else:
                print("File : " + file + " does not exists or file isn't of type .json.")
        return ret_arr            

    
########## Template Search Code ##########

    ''' Fucntion responsible for reading a .tmpl file. count refers to number of files to
        records to display (Option 2, Template Search) and record is used to display a
        specific record.'''
    def read_template(self, file, count=None, record=None, out=False):
        num = 0
        prints = 0
        
        # Try statement used to catch invalid number input from user
        try:
            int(count)
        except:
            num = None

        # Print all records if user specifies * 
        if count == '*':
            num = len(self.parsed_files)
            
        contents = ""
        lines = open(file, 'r').readlines()
        
        if record == None:
            for diction in self.parsed_files:
                for line in lines:
                    # get_line returns the line to display based on .tmpl file
                    contents = contents + self.get_line(line, diction)
                print("\n" + contents)
                prints = prints + 1
                contents = ""
                
                if num != None and count != '*':
                    num = num+1
                    if num == int(count):
                       # Stop immediate home page return
                       try:
                           input("Press Enter to Continue or type Quit to break out of Search > ") 
                           return
                       except KeyboardInterrupt:
                           return

                prints = prints + 1
                # If the user types quit in the input leave the method.
                if self.check_stop(prints, 8):
                    return
                    
        else:
            # Happens when a record is specified
            for line in lines:
                contents = contents + self.get_line(line, record)
            if not out:
                print("\n" + contents)
            else:
                print(contents)
                return "\n" + contents
    

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
            if len(val) > 2:
                return diction[val[0]][val[1]][val[2]]
            elif len(val) > 1:
                return diction[val[0]][val[1]]
            elif len(val) == 1:
                return diction[val[0]]
        except:
            # Return error string if user has entered an invalid key
            return "Object '" + str(val) + "' not found."

########## End of Template Search Code ##########


########## Key Word Search Code ##########

    ''' This function is in charge of simple word search. Based on what the user inputs
        all records are searched through in either the tweet text, users screen name or
        users location.'''
    def search_word(self, word, search_type, template, out=False):
        # Allow mutli file search in future.
        prints = 0

        out_file = []

        for diction in self.parsed_files:
            try:
                if search_type == 1:
                    if word in diction['text']:
                        if out:
                            data = self.read_template(template, record=diction, out=True)
                            out_file.append(data)
                            continue
                        self.read_template(template, record=diction)    
                        prints = prints + 1
                        # If user types quit return to previous page
                        if self.check_stop(prints, 8):
                            return
                elif search_type == 2:
                    if word in diction['user']['screenName']:
                        self.read_template(template, record=diction)
                        prints = prints + 1
                        # If user types quit return to previous page
                        if self.check_stop(prints, 8):
                            return
                elif search_type == 3:
                    if word in diction['user']['location']:
                        self.read_template(template, record=diction)
                        prints = prints + 1
                        # If user types quit return to previous page
                        if self.check_stop(prints, 8):
                            return
            except Exception as e:
                 print(e)
        if out:
            return out_file
        # Stop immediate home page return
        try:
            input("Press Enter to Continue > ")
        except KeyboardInterrupt:
            return


    ''' Function responsible for parsing the word template file. It goes through each line until it finds
        the word template the user previously chose. Then it grabs all words associated with that key word.
        It does this by getting all comma seperated words inbetween the [] of that line.'''
    def parse_word_template_file(self, word, template):
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                if word in line:
                    try:
                        vals = line.split('[')[1].split(']')[0].split(',')
                        self.search_word_template(vals, template)
                        # After template has bee found return as no need to keep doing loop.
                        return
                    except:
                        print("Category " + word + " is not correctly formatted.")


    ''' Function responsible for getting results of a word template. Runs within
        parse_word_template_file() and checks to see if any word related to the template
        word is the tweet text of any records. If it is the records is printed out via
        read_template()'''
    def search_word_template(self, key_words, template):
        prints = 0
        for diction in self.parsed_files:
            for word in key_words:
                if word.lstrip().rstrip() in diction['text']:
                    self.read_template(template, record=diction)
                    prints = prints + 1
                    # If user types quit return to previous page
                    if self.check_stop(prints, 5):
                        return


    ''' Function responsible for adding a new Word Template. Takes an input from the user
        if the file exists user is returned, otherwise new template file is added with
        correct formatting.'''
    def add_word_template(self):
        try:
            name = input("Input name of new Word Template : ")

            # If template exists return the user to previous screen.
            if self.check_template_exists(name.rstrip().lstrip()):
                print("Word Template with same name allready exists.")
                return
            
            input_vals = input("Input comma seperated values related to the key word : ")
            vals = input_vals.split(',')
            with open("wordTemplates/wordTemplates.txt", 'a') as file:
                file.write("\n" + name + " ^ " + "[")
                for i in range(len(vals)):
                    file.write(vals[i])
                    # Don't add a comma to the final value.
                    if i != len(vals)-1:
                        file.write(",")
                # Close the square brackets so Word Template can be correctly parsed.
                file.write("]")
        except KeyboardInterrupt:
            return


    ''' Function responsible for deleting an existing Word Template. If the user
        specified Word Template exists write all existing data to the file,
        excluding the given template.'''
    def delete_word_template(self, display):
        try:
            temp_to_del = input("Type the name of the Word Template you want to delete : ")
        except KeyboardInterrupt:
            return
        
        # Check if word template exists.
        if temp_to_del not in display:
            print("That is not a valid Word Template")
            return

        new_file_contents = ""
        with open("wordTemplates/wordTemplates.txt", 'r') as read_file:
            for line in read_file:
                if temp_to_del in line:
                    continue
                else:
                    new_file_contents = new_file_contents + line
        with open("wordTemplates/wordTemplates.txt", 'w') as write_file:
            write_file.write(new_file_contents)

            
    ''' This function checks if a template exists within the Word Template file.
        if it does it returns True, otherwise it returns False.''' 
    def check_template_exists(self, name):
        with open("wordTemplates/wordTemplates.txt", 'r') as file:
            for line in file:
                if name.lower() in line.lower():
                    return True
        return False
        
            
                

########## End of Key Word Search Code ##########


##########  Regex Search Code ##########

    ''' Function responsible for doing a simple regex search. Takes a
        regular expression from the user and checks to see if it matches
        any of the parsed records.'''
    def simple_regex_search(self, expr, template, out=False):
        prints = 0
        out_arr = []
        for diction in self.parsed_files:
            if len(re.findall(expr, diction['text'])) > 0:
                if out:
                    data = self.read_template(template, record=diction, out=True)
                    out_arr.append(data)
                    continue
                prints = prints + 1
                self.read_template(template, record=diction)
                # If user types quit return to previous page
                if self.check_stop(prints, 5):
                    return
        if out:
            return out_arr
        # Stop immediate home page return
        try:
            input("Press Enter to Continue > ")
        except KeyboardInterrupt:
            return
                

    ''' This function reads a .expr file, parsing the expression to be used,
        the EXCEPTS and the INCLUDES.'''
    def read_expression(self, file, template):
        expr_file = open(file, 'r').readlines()
        search_location = re.findall(r'\{(.*?)\}', expr_file[0])[0]
        
        # Try to make sure that expression line is correctly formatted
        try:
            expression = expr_file[0][expr_file[0].index('^', 0, len(expr_file[0]))+1:].rstrip().lstrip()
        except:
            print("Expression File " + file + " does not have correct formatting for Expression Line")
            return
        
        exceptions = None
        includes = None
        # Get EXCEPTS in file.
        if len(expr_file) > 1:
            if expr_file[1].startswith("EXCEPT"):
                exceptions = self.get_regex_excep(expr_file[1])
            elif expr_file[1].startswith("PASS"):
                pass
            else:
                print("Invalid Syntax in EXCEPT Line.")

        # Get INCLUDES in file.     
        if len(expr_file) > 2:
            if expr_file[2].startswith("INCLUDE"):
                includes = self.get_regex_includes(expr_file[2])
            else:
                print("Invalid Syntax in INCLUDE Line.")
        
        self.regex_search(expression, search_location, template, exceptions, includes)


    ''' Function responsible for parsing the EXCEPTS of a .expr file. Two arrays are returned
        one stating the field the EXCEPT is targeting, e.g. username, and the other the value
        that the should be EXCEPTED related to the field, e.g. Bob Smith.'''
    def get_regex_excep(self, line):
        fields = [] # Fields to check
        values = [] # Values to check

        # Each EXCEPT ends with a ';' hence the for loop and split here.
        for item in line.split(';'):
            # Regular expression to parse data between {}
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
    def regex_search(self, expr, field, template, exceptions, includes):
        prints = 0
        counter = 0
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
                prints = prints + 1
                counter += 1
                self.read_template(template, record=diction)
                if includes != None:
                    if "RESULT" in includes:
                        print("Results : " + str(result))

                    if "EXPRESSION" in includes:
                        print("Expression Used : " + str(expr))

                    if "COUNTER" in includes:
                        print("Record Number : " + str(counter))
                
                # If user types quit return to previous page
                if self.check_stop(prints, 5):
                    return
                
        # Stop immediate home page return
        try:
            input("Press Enter to Continue > ")
        except KeyboardInterrupt:
            return


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
                    print("Key Error in EXCEPT Line.")
                    return "ERROR"
                    
            else:
                # Single key (no sub dicts) search.
                if diction[exceptions[0][i]] == exceptions[1][i]:
                    return True
                
        # If no EXCEPTS match return False, record can now be displayed. 
        return False
                

########## End of Regex Search Code ##########


##########  User Search Code ##########

    ''' Function responsible for checking if a given user exists, getting
        user data if they do.'''
    def user_search(self, username, out=False):
        for diction in self.parsed_files:
            if diction['user']['name'] == username:
                if out:
                    data = self.get_user_data(username, out=True)
                    return data
                self.get_user_data(username)
                return
            else:
                pass
        # If specified user doesn't exists in parsed records, show error.
        print("User " + username + " Does not Exist.")


    ''' Function responsible for get user data and displaying it to the user.
        If the username matches variables are set to the relvant information
        about that user.'''
    def get_user_data(self, username, out=False):
        date_joined = ""
        num_of_tweets = 0
        num_of_sensitive_tweets = 0
        follwers = 0
        location = ""
        desc = ""
        for diction in self.parsed_files:
            if diction['user']['name'] == username:
                num_of_tweets = num_of_tweets + 1
                if diction['isPossiblySensitive']:
                    num_of_sensitive_tweets = num_of_sensitive_tweets + 1
                date_joined = str(diction['user']['createdAt']['$date'])
                followers = diction['user']['followersCount']
                location = diction['user']['location']
                # Not all users have a description resulting in key crash
                try:
                    desc = diction['user']['description']
                except:
                    desc = "No Description Found"

        if out:
            return "Name : " + username + "\nDescription : " + desc + "\nDate Joined : " + date_joined[:10] +"\nFrom : " + location + "\nNumber of Tweets : " + str(num_of_tweets) +"\nNumber of Sensitive Tweets : " + str(num_of_sensitive_tweets) + "\nNumber of Followers : " + str(followers)
        print("\n\nName : " + username + "\nDescription : " + desc + "\nDate Joined : " + date_joined[:10])
        print("From : " + location)
        print("Number of Tweets : " + str(num_of_tweets))
        print("Number of Sensitive Tweets : " + str(num_of_sensitive_tweets))
        print("Number of Followers : " + str(followers))
        
        try:
            input("Press Enter to Continue > ") # Stop from auto reseting to home screen
        except KeyboardInterrupt:
            return
                
                
                
                
                

########## End of User Search Code ##########

    ''' Function responsible for writing data to a given file. ext refers to extension
        file will be given and path refers to where it will be saved. This data is
        passed with CDDisplay.py'''          
    def write_to_file(self, path, ext):
        try:
            file_name = input("Name for new file : ")
            
            # If file name already exists return and show error.
            if os.path.isfile(path + file_name + "." + ext):
                print("File with same name already exists")
                return
            
            print("To stop file template end line with '~'.")
            content = ""
            line = input()

            # User must terminate the file with specified character ~
            while not line.endswith("~"):
                content = content + line + "\n"
                line = input()
            content = content + line
        except KeyboardInterrupt:
            return

        # Write to data file and then close it when done.    
        new_file = open(path + file_name + "." + ext, 'w')
        new_file.write(content.rstrip()[:-1])
        new_file.close()


    ''' Function responsible for deleting files. Unlike write_to_file(),
        extension is passed within the path variable.'''
    def delete_file(self, path):
        try:
            file = input("Type out the full name of the file to be deleted (including extension) : ")
            # If specified file is a file check if the user wants to delete it.
            if os.path.isfile(path + file):
                confirm = input("Are you sure you want to delete " + file + "? (y/n)")
                if confirm[0].lower() == 'y':
                    os.remove(path + file)
                    print("File " + file + " Deleted")
                else:
                    print("No Files Deleted")
            else:
                print("That file does not exist")
        except KeyboardInterrupt:
            return


    ''' This function is used a lot throughout the program. Basically it prints
        out a number of records specified by the stop variable and compares it to
        the current number of printed records. It is also handy as the user is able
        to break out of records being displayed by entering 'quit'.'''
    def check_stop(self, prints, stop):
        try:
            if prints % stop == 0:
                ui = input("Press Enter to Continue or Type Quit to Break Out >  \n")
                if ui.lower() == "quit":
                    return True
                else:
                    return False
        except KeyboardInterrupt:
            return True






