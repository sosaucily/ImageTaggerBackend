# This is part of the ImageTagger Backend Database Management System
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

# MongoFactory
# This can be imported to build and maintain mongo connections

from imagetaggerlib import imagetagger_tools as Tools
from cherrypy import log as cherrylog
from pymongo import Connection
from pymongo.objectid import ObjectId as oid
import sys, os, datetime
import config as c

class MongoFactory(object):
	
	def __init__(self, collection=""):
		"""Constructor"""
		self.mongo_connection = Connection() #This gets closed by the parent destructor
		self.bettermedia = self.mongo_connection['BetterMedia']  # `BetterMedia` database
		self.betterkeyword = self.mongo_connection['BetterKeyword']
		self.image_collection = self.bettermedia.image  # `image` collection
		self.video_collection = self.bettermedia.video  # `video` collection
		self.scene_collection = self.bettermedia.scene  # `scene` collection
		#self.keyword_collection = self.betterkeyword.keyword # 'keyword' collection
		
	def __del__(self):
		"""Mongo connection descructor
		
		Tear down Mongo connection object if set.
		
		"""
		if (self.mongo_connection != ""):
			self.mongo_connection.disconnect()