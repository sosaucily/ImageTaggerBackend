# This is part of the ImageTagger Keyword and Category management system
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

# MSegment (Media Segment)
# This is the parent class of the MScene, MVideo, and MImage classes.
# It is primarily used to provide an interface for creating and updating objects
# These objects provide access to keyword and category data for these objects.

# Analysis to performance data and Ad Inventory data will likely be designed into separate systems.
#from imagetaggerlib.media import m_segment as m, m_image as mi
from imagetaggerlib import imagetagger_tools as Tools
from imagetaggerlib import mongo_document as MD
from cherrypy import log as cherrylog
import sys, os, datetime
import config as c
#from imagetaggerlib.media_process_sources import *

class MSegment(MD.MongoDocument):
				
	skip_entire_words = []
	
	skip_any_part_of_phrase = ["unclear","none","nothing"]
	
	