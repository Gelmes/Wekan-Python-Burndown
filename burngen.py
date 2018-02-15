# burngen.py
# Author: Marco Rubio
# Date  : 2/14/2018
# Desc  : Creates a burn down plot from the wekan mongodb data

from pymongo import MongoClient
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import time                         # time.strptime # For datetime compairons
import re

## Generate a burndown chart from any wekan server.
#  Multiple charts can be made for each Board and multiple boards can be
#  concatinated to give you a bigger perspective of a project.
#
#  Total hours are taken from all cards of a given board.
#  Time left is calculated given the cards under the list with the word
#  'done' in its title.
#
#  current implementations are case insensative.
#  usage: TBA
class BurnChart:

    def __init__(self, url='localhost', port=27019):
        # Configuration Variables
        self.URL  = url     # URL of wekan server
        self.PORT = port    # Port of mongodb database
        self.client = MongoClient(self.URL, self.PORT)
        self.db = self.client.wekan


    ## Get number in parenthesis or return 0
    #
    #  @param  string String to parse for parenthesis database
    #  @return intiger contained in parenthesis
    def get_parenthesis(self, string):
        start = string.find("(") # Verify we have (
        end   = string.find(")") # Verify we have )
        value= 0
        if(start != -1):
            if(end != -1):
                value= int(string[start+1:end])
        return value

    ## Get the board id given its title
    #
    #  @param  title        Title to search format
    #  @param  whole_word   Should the title match 100%, set to 1 if true
    #  @return string containing the board id
    def get_board_id(self, title, whole_word=0):
        if(whole_word):     # Find a board that matches title 100%
            board = self.db.boards.find({'title':title})
        else:               # Find any board with the title included
            regx = re.compile(".*"+title+".*", re.IGNORECASE)
            board = self.db.boards.find({'title':regx})

        return board[0]['_id']

    ## Get the list id containing the title.
    #
    #  @param  title       Title to search format
    #  @param  board_id    Board to look under
    #  @param  whole_word  Should the title match 100%, set to 1 if true
    #  @return string containing the lsit id
    def get_list_id(self, title, board_id="", whole_word=0):
        if(whole_word):     # Find a list that matches title 100%
            lst = self.db.lists.find({'title':title})
        else:               # Find any list with the title included
            regx = re.compile(".*"+title+".*", re.IGNORECASE)
            lst = self.db.lists.find({'title':regx}, {'boardId':board_id})

        return lst[0]['_id']

    ## Get the cards contained in ether or the given board and/or list
    #
    #  @param  board_id    Board to look under
    #  @param  list_id     List to look under
    #  @return array of card objects
    def get_cards(self, board_id="", list_id=""):
        if(list_id == "" and board_id==""):
            cards = self.db.cards.find()
        elif(list_id == ""):
            cards = self.db.cards.find({'boardId':board_id})
        elif(board_id == ""):
            cards = self.db.cards.find({'listId':list_id})
        else:
            cards = self.db.cards.find({'listId':list_id,'boardId':board_id})
        return cards

    ## Create a timeline numpy arrays from the provided cards.
    #
    #  Sorting is generated using sort_by and  also used to create daily
    #  progress running total. The generated timeline will use the parenthesis
    #  values to calculate the running total. commont sorting values would be
    #  `createdAt` and `dateLastActivity`.
    #
    #  @param cards    input card cursor object array to convert
    #  @param sort_by  string of value to sort by
    #  @return tupple containing the dates and running total
    def create_timeline(self, cards, date_column):
        dates  = [datetime.datetime(2000,1,1)]  # Start from a date before 9/11
        total  = [0]
        for card in cards:
            expected = self.get_parenthesis(card['title'])
            if(expected):
                if(card[date_column].date() > dates[-1].date()):
                    dates.append(card[date_column])
                    total.append(total[-1]+expected)
                else:
                    total[-1] += expected
        dates.pop(0) # Remove the initial dummy element
        total.pop(0) # Remove the initial dummy element
        return np.array(dates), np.array(total) # Convert to numpy arrays

    ## Generate a plot from the provided data
    #
    #  The data is expected to be formated in tupple form with the dates as
    #  the first element and the running total as the second element
    #  @param  data data with date as first element and running total as second
    def create_plot(self, data):
        # Extract data so its easier to identify
        dates = data[0]
        total = data[1]

        # Locate specific markers for generating tick markers later
        #days = mdates.DayLocator()              # every day
        #hours = mdates.HourLocator(interval=6)  # every 6 hours
        #dayFmt = mdates.DateFormatter('%b-%d')

        # Create our plots
        fig, ax = plt.subplots()
        ax.plot(dates, total)

        # format the ticks
        #ax.xaxis.set_major_locator(days)
        #ax.xaxis.set_major_formatter(dayFmt)
        #ax.xaxis.set_minor_locator(hours)

        # Get maximum points to scale things properly
        fst = dates.min()
        snd = dates.max()
        datemin = datetime.date(fst.year, fst.month, fst.day)
        datemax = datetime.date(snd.year, snd.month, snd.day)
        ax.set_xlim(datemin, datemax)

        # format the coords message box
        def price(x):
            return '%1f Hours' % x

        # Format the axis labels
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        plt.show()


    ## Adds burn down chart to current list of burndown charts
    #
    #  @param  board_title board title to get content from
    def create_chart(self, board_title):
        # Get board id and the 'done' list id
        board_id = self.get_board_id(board_title)
        done_list_id = self.get_list_id("done", board_id)

        # Get cards
        #cards = self.get_cards(board_id).sort("createdAt")
        done_cards = self.get_cards(board_id, done_list_id).sort("dateLastActivity")

        """
        print(board_id)
        print(done_list_id)
        for card in done_cards:
            print(card['title'])
        done_cards.rewind()
        """

        # Create timeline
        data = self.create_timeline(done_cards, "dateLastActivity")

        # Create plots
        self.create_plot(data)



    ## Renders/draws the charts that are in the list of burndown charts
    def render(self):
        pass

if __name__ == "__main__":
    BC = BurnChart()
    BC.create_chart("Module Polishing")
