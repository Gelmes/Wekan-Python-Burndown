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

class BurnChart:
    """ Generate a burndown chart from any wekan server. Multiple charts can
    be made for each Board and multiple boards can be concatinated to give
    you a bigger perspective of a project.

    Total hours are taken from all cards of a given board.
    Time left is calculated given the cards under the list with the word 'done' in its title.

    current implementations are case insensative.
    usage: TBA
    """
    def __init__(self, url='localhost', port=27019):
        # Configuration Variables
        self.URL  = url     # URL of wekan server
        self.PORT = port    # Port of mongodb database
        self.client = MongoClient(self.URL, self.PORT)
        self.db = self.client.wekan

    def get_parenthesis(self, string):
        """
        Get number in parenthesis or return 0

        @param  string String to parse for parenthesis database
        @return intiger contained in parenthesis
        """
        start = string.find("(") # Verify we have (
        end   = string.find(")") # Verify we have )
        value= 0
        if(start != -1):
            if(end != -1):
                value= int(string[start+1:end])
        return value

    def get_board_id(self, title, whole_word=0):
        """
        Get the board id given its title

        @param  title        Title to search format
        @param  whole_word   Should the title match 100%, set to 1 if true
        @return string containing the board id
        """
        if(whole_word):     # Find a board that matches title 100%
            board = self.db.boards.find({'title':title})
        else:               # Find any board with the title included
            regx = re.compile(".*"+title+".*", re.IGNORECASE)
            board = self.db.boards.find({'title':regx})

        return board[0]['_id']

    def get_list_id(self, title, board_id="", whole_word=0):
        """
        Get the list id containing the title.

        @param  title       Title to search format
        @param  board_id    Board to look under
        @param  whole_word  Should the title match 100%, set to 1 if true
        @return string containing the lsit id
        """
        if(whole_word):     # Find a list that matches title 100%
            lst = self.db.lists.find({'title':title})
        else:               # Find any list with the title included
            regx = re.compile(".*"+title+".*", re.IGNORECASE)
            lst = self.db.lists.find({'title':regx}, {'boardId':board_id})

        return lst[0]['_id']

    def get_cards(self, board_id="", list_id=""):
        """
        Get the cards contained in ether or the given board and/or list

        @param  board_id    Board to look under
        @param  list_id     List to look under
        @return array of card objects
        """
        if(list_id == "" and board_id==""):
            cards = self.db.cards.find()
        elif(list_id == ""):
            cards = self.db.cards.find({'boardId':board_id})
        elif(board_id == ""):
            cards = self.db.cards.find({'listId':list_id})
        else:
            cards = self.db.cards.find({'listId':list_id,'boardId':board_id})

        return cards

    def create_timeline(self, data):
        pass

    def create_chart(self, board_title):
        """
        Adds burn down chart to current list of burndown charts

        @param  board_title board title to get content from
        """
        # Get board id and the 'done' list id
        board_id = self.get_board_id(board_title)
        done_list_id = self.get_list_id("done", board_id)

        # Get cards
        cards = self.get_cards(board_id).sort("createdAt")
        done_cards = self.get_cards(board_id, done_list_id).sort("dateLastActivity")

        print(board_id)
        print(done_list_id)
        for card in done_cards:
            print(card['title'])


    def render(self):
        """ Renders/draws the charts that are in the list of burndown charts """


if __name__ == "__main__":
    BC = BurnChart()
    BC.create_chart("Module Polishing")
