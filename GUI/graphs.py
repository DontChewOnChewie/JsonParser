import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import pprint

class Graphs:

    ''' Initialise Graphs object. '''
    def __init__(self, parser):
        self.parser = parser


    ''' Function to create a pie chart of sensitive tweets vs
        non-sensitive tweets based on search results. '''
    def sensitive_tweets_pie(self):
        sensitive = 0
        # Clear previous chart data.
        plt.cla()
        plt.clf()
        plt.close()
        
        for diction in self.parser.results:
            if diction['isPossiblySensitive']:
                sensitive+=1
        vals = [sensitive, len(self.parser.results) - sensitive]
        colours = ['yellowgreen', 'gold'] # Colours to use in chart.
        # Labels for legend.
        lbls = ["Sensitive (" + str(sensitive) + ")" ,
                "Non-Sensitive (" + str(len(self.parser.results) - sensitive) + ")"]

        patches, texts = plt.pie(vals, colors=colours, startangle=90)
        plt.legend(patches, lbls, loc="best")
        return FigureCanvasKivyAgg(plt.gcf())


    ''' Function to create a line graph showing tweets made on each day
        in the search results array. '''
    def date_based_line(self):
        dates = []
        values = []
        # Clear previous chart data.
        plt.cla()
        plt.clf()
        plt.close()
        for diction in self.parser.results:
            # If new date add it to the list.
            if diction['createdAt']['$date'][5:10] not in dates:
                dates.append(diction['createdAt']['$date'][5:10])
                values.append(1)
            else:
                values[dates.index(diction['createdAt']['$date'][5:10])] += 1

       
        plt.plot(dates, values)
        return FigureCanvasKivyAgg(plt.gcf())


    ''' Function to create a bar chart that shows the most used words
        from a search result. '''
    def most_used_words_bar(self):
        words = [] # All words used.
        most_used_words = ["", "", "", "", ""] # Top 5 words used.
	# Words to exclude from search.
        common_words = ['i', 'on', 'your', 'you', 'am', 'the', 'he', 'him', 'they',
                        'her', 'she', 'it', '@', 'in', 'and', 'my', 'to', 'with', '?'
                        '.', ',', '!', 'is', 'me', 'it\'s', 'its', 'a', 'them', 'by']
        values = [] # Amount of time words used.
        most_used_values = [0,0,0,0,0] # Most used words totals.
		
        # Clear previous chart data.
        plt.cla()
        plt.clf()
        plt.close()
		
        for diction in self.parser.results:
	    # split to get words.
            for word in diction['text'].split(" "):
                # If word not common word and new word, add to list.
                if word.lower() not in common_words and word.lower() not in words:
                    words.append(word.lower())
                    values.append(1)
                # If word already in words, add to count.
                elif word.lower() in words:
                    values[words.index(word.lower())] += 1
        
	# Sort word and count arrays.
        for i in range(len(values)):
            for j in range(len(most_used_values)):
                if values[i] > most_used_values[j]:
                    most_used_values[j] = values[i]
                    most_used_words[j] = words[i]
                    break

        plt.bar(most_used_words, most_used_values)
        return FigureCanvasKivyAgg(plt.gcf())






    
