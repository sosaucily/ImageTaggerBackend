# This is part of the ImageTagger Backend Database Management System
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

# MongoDocument
# This is inherited by Media objects (MScene, MVideo, and MImage) as well as crowd/CV classes (CrowdFlower and IQEngines).
# Any object type that needs to be persistent in the Mongo Database can inherit from this class.

from imagetaggerlib import imagetagger_tools as Tools
from cherrypy import log as cherrylog
from pymongo import Connection
from pymongo.objectid import ObjectId as oid
import sys, os, datetime
import config as c

class MongoDocument(object):
	""" Class to be inherited for objects that need Mongo persistence functionality """
		
	#attributes = {} #Holds the important data for this object.  This will be persisted to the Mongo DB.
	#doc_id = "" #Holds a reference to the mongo document ID
	
	def __init__(self, collection=""):
		"""Constructor"""
	  	cherrylog ("Created Media Object of type: " + str(self.__class__.__name__))
		#Mongo Stuff - For safety / performance, these aren't always instantiated upon object instatiated and need to be built when needed.
		self.mongo_connection = "" #Mongo connection object
		self.my_collection = collection #Take a collection object if one is given.
		self.bettermedia = "" #Mongo BetterMedia database
		self.attributes = {} #Holds the important data for this object.  This will be persisted to the Mongo DB.
		self.doc_id = "" #Holds a reference to the mongo document ID
	
	def __del__(self):
		"""Mongo Object descructor
		
		Tear down Mongo connection object if set.
		
		"""
		if (self.mongo_connection != ""):
			self.mongo_connection.disconnect()
		
	def create(self):
		self.doc_id = ""
		"""Insert the object into the mongodb.  It should not exist in mongo before this call."""
		if (not self.attributes.has_key('created_at')):
			self.attributes['created_at'] = datetime.datetime.now()
		self.attributes['status'] = {'imagetagger_status':'created'}
		self.attributes['modified_at'] = datetime.datetime.now()
		cherrylog ("Creating item in database with values " + str(self.attributes))
		#insert a doc
		try:
			insert = self.my_collection.insert(self.attributes, safe=True)
		except Exception as e:
			Tools.print_errors ("Error inserting object into database: " + str(self.__class__.__name__))
			return False
		cherrylog ("Insert of item successul: " + (str(insert)))
		self.doc_id = str(insert)
		return True
	
	def load(self, lookup_doc_id=None, alt_matching={}):
		"""Load data from database into object in memory
		
		Arguments:
		lookup_doc_id -- the doc_id of the object that will be used for matching.
		alt_matching -- An alternate dictionary for doing the lookup.
		One of these two parameters is required.
		
		"""
		if (lookup_doc_id != None):
			cherrylog ("Loading " + str(self.__class__.__name__) + " with params: id=" + str(lookup_doc_id))
		else:
			cherrylog ("Loading " + str(self.__class__.__name__) + " with params: " + str(alt_matching))
		try:
			match_param = {}
			if (alt_matching != {}):
				match_param = alt_matching
			else:
				match_param = {'_id':oid(lookup_doc_id)}
			docs = self.my_collection.find(match_param, safe=True)
			cherrylog ("got number of results as: " + str(docs.count()))
			if (docs.count() == 0):
				cherrylog ("Couldn't load object, 0 matching results in database!!")
				return False
			if (docs.count() == 1):
				self.doc_id = str(docs[0]['_id'])
				if docs[0].has_key('_id'): del docs[0]['_id']
				self.attributes = docs[0]
				return True
			else:
				raise Exception("Retrieved multiple videos when only 1 was expected")
		except Exception as e:
			Tools.print_errors ("Unable to load " + str(self.__class__.__name__) + " from database with params: id=" + str(self.doc_id))
			return False
		cherrylog ("Successfully loaded object: " + str(self.attributes))
		return True
	
	def update(self, merge_data={}, commit=True):
		""" Update object with current data into mongo. 
		
		Arguments:
		merge_data -- dictionary used to represent the entire object.  This will overwrite the object's current data.
		commit -- Should this update of the data in memory be commited to mongo?  Default: True
		
		"""
		if (not merge_data=={}):
			self.merge_data(merge_data) #Intelligently merge the argument into the self.attributes variable
			cherrylog ("Data merged into object: "+ str(merge_data))
		if (commit):
			self.attributes['modified_at'] = datetime.datetime.now()
			cherrylog ("updating item in database")
			try:
				update = self.my_collection.update({'_id':oid(self.doc_id)}, self.attributes, safe=True)
			except Exception as e:
				Tools.print_errors ("Error updating object in database: " + str(self.__class__.__name__))
				return False
			cherrylog ("Update of item successul: " + (str(update)))
		return True

	#This function updates the object in memory only (self.attributes variable)
	#Recursively merges dictionary data into self.attributes
	def merge_data(self, merge_data):
		"""Deep dictionary merge of argument data into in-memory object data."""
		cherrylog ("Updating object attributes with values: " + str(merge_data) )
		MongoDocument.recursive_merge_data(self.attributes, merge_data)
		cherrylog ("Successfully updated object: " + str(self.attributes))
		return True
		
	@classmethod
	def recursive_merge_data(derived_class, original, updated):
		"""Recursive class function to move deep into dictionary and merge contents."""
		try:
			if (len(updated.keys()) == 0):
				return {}
			for key in updated.keys():
				if (original.has_key(key)) and (type(original[key]) is dict) and (type(original[key]) is dict):
					original[key] = MongoDocument.recursive_merge_data(original[key],updated[key])
				else:
					original[key] = updated[key]
		except:
			Tools.print_errors ("Error recursively updating object")
			return None
		return original