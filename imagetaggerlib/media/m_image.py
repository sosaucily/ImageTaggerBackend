# This is part of the ImageTagger Keyword and Category management system
#
# Author::    Dmitri Skjorshammer 
# Copyright:: Copyright (c) 2012 ImageTagger

# MImage (Media Image)
# This class is used to manage image level methods and data.
# It is primarily used to provide an interface for creating and updating objects
# These objects provide access to keyword and category data for these objects.

# All consideration for NLP and Keyword Market Value should be considered in this class
# and therefore won't need to be considered in other upstream classes

# Analysis to performance data and Ad Inventory data will likely be designed into separate systems.


# TO DO:
#1. Change adwordtrie code to adapt to new trie tree.
#2. Change wildcard for trie tree to fit new trie tree.
#3. Change .csv files to include Keyword Market Value.
#4. Actually run the code to see that .rb -> .py was correct
from imagetaggerlib import imagetagger_tools as Tools
from imagetaggerlib.media import m_segment as m
#from imagetaggerlib import better_trie
from cherrypy import log as cherrylog
import os, sys
from nltk.corpus import wordnet # If you don't have corpus installed, run nltk.download() in the python console


class MImage(m.MSegment): 
	
	def __init__(self, collection=""):
		"""docstring for %s"""
		super(MImage,self).__init__(collection=collection) #Call parent init method.

