# This is part of the ImageTagger Keyword and Category management system
#
# Author::    Dmitri Skjorshammer  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

# MScene (Media Scene)
# This class is used to manage scene level methods and data.
# It is primarily used to provide an interface for creating and updating objects
# These objects provide access to keyword and category data for these objects.

# All consideration for NLP and Keyword Market Value is considered to be included in MImage keyword associated value, and thus 
# doesn't need to be considered in this class.

# Analysis to performance data and Ad Inventory data will likely be designed into separate systems.
from imagetaggerlib.media import m_segment as m, m_image as mi
from cherrypy import log as cherrylog
from pymongo import Connection
import sys, os, datetime
import config as c
from imagetaggerlib.video_process import scene_detection
from imagetaggerlib.media import m_segment as m
import operator
from imagetaggerlib import mongo_factory as mongo_fac



class MScene(m.MSegment):


	COMMANDS = ['retrieve']
	SUBMIT_PARAMS = ['friendly_id','display_name','video_description', 'video_meta_tags','account_id']
	LOOKUP_PARAMS = ['friendly_id']
	UPDATE_PARAMS = ['file_name','file_type','length','hashstring','width','height','source_metadata','better_metadata']

	@staticmethod
	def validate_cmd(cmd):
		if (cmd not in MScene.COMMANDS):
			cherrylog ("Invalid Command for Scene " + str(cmd))
			return False
		else:
			return True

	@staticmethod
	def get_valid_commands():
		return MScene.COMMANDS


