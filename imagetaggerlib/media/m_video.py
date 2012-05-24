# This is part of the ImageTagger Keyword and Category management system
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

# MVideo (Media Video)
# This class is used to manage video level methods and data.
# It is primarily used to provide an interface for creating and updating objects
# These objects provide access to keyword and category data for these objects.

# All consideration for NLP and Keyword Market Value is considered to be included in MImage keyword associated value, and thus 
# doesn't need to be considered in this class.

# Analysis to performance data and Ad Inventory data will likely be designed into separate systems.
from imagetaggerlib.media import m_segment as m, m_image as mi, m_scene as ms
from cherrypy import log as cherrylog
from pymongo import Connection
import sys, os, datetime, glob, shutil
import config as c
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2, urllib
from imagetaggerlib import keyword_tools as Keywords
#from imagetaggerlib.video_process import video_process as vp
from imagetaggerlib.media_process_sources import *
from imagetaggerlib import report
from imagetaggerlib import imagetagger_tools as Tools
		
class MVideo(m.MSegment):

	COMMANDS = ['submit','retrieve','update','analyze','get_images','reprocess_metadata','rebuild_report','destroy']
	SUBMIT_PARAMS = ['friendly_id','display_name','video_description', 'video_meta_tags','account_id']
	LOOKUP_PARAMS = ['friendly_id']
	UPDATE_PARAMS = ['file_name','file_type','length','hashstring','width','height','source_metadata','better_metadata']
	ANALYZE_PARAMS = ['friendly_id','quality']
	REPROCESS_PARAMS = ['friendly_id']
	REBUILD_PARAMS = ['friendly_id','quality']

	@staticmethod
	def validate_cmd(cmd):
		if (cmd not in MVideo.COMMANDS):
			cherrylog ("Invalid Command for Video " + str(cmd))
			return False
		else:
			return True
	
	@staticmethod
	def validate_submit_params(video_json):
		if not all (k in video_json for k in (MVideo.SUBMIT_PARAMS)):
			cherrylog ("Video submit is missing a parameter")
			return False
		if len(video_json.keys()) != len(MVideo.SUBMIT_PARAMS):
			cherrylog ("wrong number of parameters for video ")
			return False
		return True

	@staticmethod
	def validate_retrieve_params(video_json):
		if not all (k in video_json for k in (MVideo.LOOKUP_PARAMS)):
			cherrylog ("Video lookup is missing a parameter")
			return False
		if len(video_json.keys()) != len(MVideo.LOOKUP_PARAMS):
			cherrylog ("wrong number of parameters for video ")
			return False
		return True
		
	@staticmethod
	def validate_update_params(video_json):
		if not all(k in MVideo.UPDATE_PARAMS for k in video_json):
			cherrylog ("Video update parameter is not valid")
		#if not all (k in video_json for k in (MVideo.UPDATE_PARAMS)):
		#	cherrylog ("Video update is missing a parameter")
		#	return False
		#if len(video_json.keys()) != len(MVideo.UPDATE_PARAMS):
		#	cherrylog ("wrong number of parameters for video ")
		#	return False
		return True

	@staticmethod
	def validate_analyze_params(video_json):
		if not all (k in video_json for k in (MVideo.ANALYZE_PARAMS)):
			cherrylog ("Video lookup is missing a parameter")
			return False
		if len(video_json.keys()) != len(MVideo.ANALYZE_PARAMS):
			cherrylog ("wrong number of parameters for video ")
			return False
		return True

	@staticmethod
	def validate_reprocess_metadata_params(video_json):
		if not all(k in MVideo.REPROCESS_PARAMS for k in video_json):
			cherrylog ("Video reprocessMetadata command is missing params")
			return FALSE
		if len(video_json.keys()) != len(MVideo.REPROCESS_PARAMS ):
			cherrylog("Video reprocessMetadata command: wrong number of params")
			return False
		return True

	@staticmethod
	def validate_rebuild_report_params(video_json):
		if not all(k in MVideo.REBUILD_PARAMS for k in video_json):
			cherrylog ("Video rebuildReport command is missing params")
			return FALSE
		if len(video_json.keys()) != len(MVideo.REBUILD_PARAMS ):
			cherrylog("Video rebuildReport command: wrong number of params")
			return False
		return True
	
	@staticmethod
	def get_valid_commands():
		return MVideo.COMMANDS
	
	@staticmethod
	def get_required_submit_params():
		return MVideo.SUBMIT_PARAMS
	
		
#class attributes (in database mongo)
#ID, length, categories, keywords, bunhc of cached ads.

	def __init__(self):
		"""Initialize MVideo object.
		
		Set up the Mongo connection objects.
		
		"""
		cherrylog ("Created Media Object of type: " + str(self.__class__.__name__))
		self.mongo_connection = Connection() #This gets closed by the parent destructor
		self.bettermedia = self.mongo_connection['BetterMedia']  # `BetterMedia` database
		self.image_collection = self.bettermedia.image  # `image` collection
		self.scene_collection = self.bettermedia.scene
		self.my_collection = self.bettermedia.video  # `video` collection
		self.attributes = {} #Holds the important data for this object.  This will be persisted to the Mongo DB.
		self.doc_id = "" #Holds a reference to the mongo document ID


	def destroy(self):
		cherrylog ("Deleting video from database")
		#Don't delete the video in the database, as it contains our useful metadata.
		#It has unique idenfitiers, so it should never clash
			#match_param = {'friendly_id':self.attributes['friendly_id']}
			#self.my_collection.remove(match_param)
		#Instead, mark the video as deleted
		self.update({'status':{'imagetagger_status':'deleted'}}, commit=True)
		#For now, don't delete other metadata about the video
			#match_param = {'video':self.attributes['friendly_id']}
			#self.scene_collection.remove(match_param)
			#self.image_collection.remove(match_param)
		
		#Should check if there are active crowd services, and if so, cancel them.
		self.delete_data()
		cherrylog ("Done destroying video")

	def delete_data(self):
		cherrylog ("Removing Video files, including hidden files (.*)")
		video_root_dir = c.configs['imagetagger']['processed_videos_dir'] + "/" + self.attributes['hashstring']
		#image_files = glob.glob(video_root_dir + '/' + c.configs['imagetagger']['image_dir_name'] + '/*') + glob.glob(video_root_dir + '/' + c.configs['imagetagger']['image_dir_name'] + '/.*')
		#video_files = glob.glob(video_root_dir + '/' + c.configs['imagetagger']['video_dir_name'] + '/*') + glob.glob(video_root_dir + '/' + c.configs['imagetagger']['video_dir_name'] + '/.*')
		#report_files = glob.glob(video_root_dir + '/' + c.configs['imagetagger']['report_dir_name'] + '/*') + glob.glob(video_root_dir + '/' + c.configs['imagetagger']['report_dir_name'] + '/.*')
		try:
			#Have to first delete all files, when using the OS lib
			#for image_count in range(len(image_files)):
			#	os.remove(image_files[image_count])
			#for video_count in range(len(video_files)):
			#	os.remove(video_files[video_count])
			#for report_count in range(len(report_files)):
			#	os.remove(report_files[report_count])
			
			#os.removedirs(video_root_dir)
			shutil.rmtree(video_root_dir)
		except OSError:
			Tools.print_errors("Unable to delete directory or files in " + c.configs['imagetagger']['processed_videos_dir'] + "/" + self.attributes['hashstring'])
		
	def send_thumbnail_to_web(self, processedVideoPath, video_stats, thumb_dir, thumb_name):
		cherrylog ("Building Thumbnail PUT request")
		md5 = video_stats['hashstring']

		thumb_file_path = processedVideoPath + "/" + md5 + "/" + thumb_dir + "/" + thumb_name
		cherrylog ("thumbnail file path: " + thumb_file_path)
		
		dest_url = c.configs['imagetagger']['video_thumbnail_url'] + "/videos/" + str(self.attributes['friendly_id'])
		cherrylog ("dest url is: " + dest_url)

		# Register the streaming http handlers with urllib2
		register_openers()

		params = {"remote_key":c.configs['imagetagger']['remote_key']}
		datagen, headers = multipart_encode([("thumbnail",open(thumb_file_path, "rb") )])
		dest_url += "?" + urllib.urlencode(params)
		# Create the Request object
		request = urllib2.Request(dest_url, datagen, headers)
		request.get_method = lambda: 'PUT'
		# Actually do the request, and get the response
		cherrylog ("Sending Thumbnail update to imagetagger web")
		print urllib2.urlopen(request).read()		
		cherrylog ("Done!")
		return True
 		#processedVideoPath, md5, thumb_dir, thumb_name
		
	def doProcess(self):
		cherrylog ("Processing Video with imagetagger video pre-process system")
		self.update({'status':{'imagetagger_status':'processing'}})

	def get_image_json(self):
		match_param = {'$and':[ {'video':self.attributes['friendly_id']}, {'send_to_crowd':True} ] }
		image_docs = self.image_collection.find(match_param, safe=True)
		results = []
		count = 0
		url_base = c.configs['imagetagger']['callback_URL'] + "/images/" + self.attributes['hashstring'] + "/" + c.configs['imagetagger']['image_dir_name']
		for image in image_docs:
			image_url = url_base + "/" + image['filename']
			results.append({'image_info':{'id':str(image['_id']),'url':image_url}})
			count += 1
		return (results)
		
	def flag_images_for_crowd(self, quality):
		"""docstring for flag_images_for_crowd"""
		match_param = {'video':self.attributes['friendly_id']}
		image_docs = self.image_collection.find(match_param, safe=True)
		interval = 0
		
		#Number of seconds between images to process
		if (quality == 'basic'):
			interval = 4
		elif (quality == 'premium'):
			interval = 2
		else:
			interval = 4
		
		#Expects a round integer for time_in_video
		for image in image_docs:
			if (image['time_in_video'] % interval == 0):
				cherrylog ("Flagging this image to be sent to crowd: " + str(image))
				flag_image = mi.MImage(collection=self.image_collection)
				flag_image.load(str(image['_id']))
				flag_image.update({'send_to_crowd':True})


