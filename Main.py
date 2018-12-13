import sys
import os
import re
import JsonParser as jp
import CDisplay as dis


''' Setup the program to start running by getting
    command line arguments that should be JSON files.'''
def main():
    files = []
    for i in range(1, len(sys.argv)):
        files.append(sys.argv[i])
    parser = jp.JsonParser(files)

    # Run program normally if output args not specified.
    if not check_for_output(parser):
        display = dis.CDisplay(parser)


''' Create all the needed files for the user to be able
    to run the program correctly.'''
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


''' Function used to handle the user wanting to get an output file
    from the program. The function parses all arguments passed by the user
    and if all are valid runs the correct functions in JsonParser.py to
    get output into the specified file.'''
def check_for_output(parser):
        # Check if its possible for enough arguments to output.
        if len(sys.argv) < 3:
            return False
        
        out_file = ""
        search_type = ""
        arg = ""
        template = ""
        # Parse users args.
        for i in range(2, len(sys.argv)):
            if 'output' in sys.argv[i].lower():
                out_file = str(sys.argv[i].split('=')[1].rstrip().lstrip())
            elif 'type' in sys.argv[i].lower():
                search_type = str(sys.argv[i].split('=')[1].rstrip().lstrip())
            elif 'arg' in sys.argv[i].lower():
                arg = str(sys.argv[i].split('=')[1].rstrip().lstrip())
            elif 'template' in sys.argv[i].lower():
                template = str(sys.argv[i].split('=')[1].rstrip().lstrip())

        # Check if output file allready exists.
        if os.path.exists(str(out_file)):
            print("File with same name already exists.")
            exit()

        # Set default .tmpl if none specified.
        if template == "":
            template = "templates/included/basic.tmpl"

        # Check for valid search type.
        if search_type.lower() != 'regex' and search_type.lower() != 'word' and search_type.lower() != 'user' and search_type != "":
            print("type parameter must equal 'regex' or 'word' or 'user'.")

        # All criteria is valid, output to file.
        if out_file != None and search_type != None and arg != None:
            output_data(out_file, search_type, arg, template, parser)
            return True

        return False

''' Function used to actually output the data to a file as well
    as direct the users arguments into the correct function in
    JsonParser.py.'''
def output_data(out_file, search_type, arg, template, parser):
    with open(out_file, 'w') as file:
        if search_type == 'word':
            data = parser.search_word(arg, 1, template, out=True)
            for item in data:
                file.write(item)
        elif search_type == 'regex':
            data = parser.simple_regex_search(arg, template, out=True)
            for item in data:
                file.write(item)
        elif search_type == 'user':
            data = parser.user_search(arg, out=True)
            file.write(data)


''' If the user is running the source file and not calling it
    through another file run the program. This is mainly just
    a convention of the language.'''
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        setup()
        main()
    else:
        # If no files given in cmd argument, print error
        print("Please enter a file to analyse; e.g python FileAnalyser.py file.json")

