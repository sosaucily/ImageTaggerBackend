#!/usr/bin/env python

# This is part of the ImageTagger Crowd and CV connection system
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

from cherrypy import log as cherrylog
from imagetaggerlib import mongo_document as MD
from pymongo import Connection
import os, simplejson, sys, datetime
import re
from imagetaggerlib import imagetagger_tools as Tools

class MediaProcess(MD.MongoDocument):
	'''Base class for managing connections to Crowd and CV systems'''
		
	def __init__(self):
		cherrylog("Buiding Media Process object")
		super(MediaProcess,self).__init__() #Call parent init method.
		self.source_name = ""
		self.mongo_connection = Connection() #This gets torn down in the parent's destructor
		self.bettermedia = self.mongo_connection['BetterMedia']  # `BetterMedia` database
		self.my_collection = self.bettermedia.crowdservice  # `crowdservice` collection

	def sanitize_items_results(self, input_array):
		try:
			if (input_array == None):
				return None
			clean_array = []
			for item in input_array:
				if (item == None):
					continue
				if (len(item) > 80):
					continue
				item_clean = str(re.sub(r'[^\w\s&]+','',item))
				item_clean.strip()
				if (len(item_clean) >= 3):
					clean_array.append(item_clean)
			
			return clean_array
			
		except Exception as e:
			Tools.print_errors ("Error sanitizing result from Crowd Source!")
			return ""
