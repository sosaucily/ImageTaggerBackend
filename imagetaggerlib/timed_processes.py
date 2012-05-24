#!/usr/bin/env python

# This is part of the ImageTaggerBackend scheduled task system
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com)
# Copyright:: Copyright (c) 2012 ImageTagger

from cherrypy import log as cherrylog
from imagetaggerlib import imagetagger_tools as Tools
import os
from video_process import video_process as vp
import config as c
import time
from imagetaggerlib.media import m_video as mv
from imagetaggerlib.video_process import scene_process as sp

class TimedProcesses():
	
	running = True
	#t = None
	#videoInputPath = ""
	#videoOutputPath = ""
	#video_dir = ""
	#image_dir = ""
	#process_videos_timer_seconds = ""
	#timed_processes_shutdown_time = ""
	registered_processes = []
	
	def __init__(self):
		self.t = ""
		self.videoInputPath = c.configs['imagetagger']['new_videos_dir']
		self.videoOutputPath = c.configs['imagetagger']['processed_videos_dir']
		self.video_dir = c.configs['imagetagger']['video_dir_name']
		self.image_dir = c.configs['imagetagger']['image_dir_name']
		self.report_dir = c.configs['imagetagger']['report_dir_name']
		self.thumb_dir = c.configs['imagetagger']['thumb_dir_name']
		self.thumb_name = c.configs['imagetagger']['thumb_file_name']
		self.timed_processes_shutdown_time = int(c.configs['imagetagger']['timed_processes_shutdown_time'])
		self.print_timed_process_update = int(c.configs['imagetagger']['print_timed_process_update'])
		TimedProcesses.registered_processes.append(self)

	def check_for_new_videos(self):
		cherrylog("Running: check_for_new_videos in " + self.videoInputPath)
		dirList=os.listdir(self.videoInputPath)
		cherrylog(str(len(dirList)) + " videos to process")
		for i in dirList:
			cherrylog ("Processing video " + self.videoInputPath + '/' + i)
			file_name = i.split(".")[0]
			video = mv.MVideo()
			if (not video.load(alt_matching={'friendly_id':int(file_name)})):
				cherrylog ("Error, Could not find initial entry of video in database... skipping")
				continue
			if (video.attributes['status']['imagetagger_status'] == 'created'):
				cherrylog ("Processing a new video:")
				video_stats = vp.get_video_info (self.videoInputPath,i,self.videoOutputPath, self.video_dir, self.image_dir, self.report_dir, self.thumb_dir)
				if (video_stats == None):
					cherrylog("Error processing a video with video_preprocess.  Exiting process thread.")
					video.update({'status':{'imagetagger_status':'error', 'error_message':'Video Hash Directory already exists.'}}, commit=True)
					self.running = False
					continue
				thumb_result = vp.get_thumbnail(self.videoInputPath, i, self.videoOutputPath, self.thumb_dir, self.thumb_name, video_stats)
				if (thumb_result):
					video.send_thumbnail_to_web(self.videoOutputPath, video_stats, self.thumb_dir, self.thumb_name)
				else:
					cherrylog("Couldn't generate thumbnail for video! " + i)				
				cherrylog("Updating video with: " + str(video_stats))
				video.update({'status':{'imagetagger_status':'processing'}}, commit=False)
				video.update(merge_data=video_stats, commit=True) #updates videos with data from initial video process
				cherrylog("Building image files: " + str(video_stats))
				result = vp.splice_video_into_images (self.videoInputPath, i, self.videoOutputPath, self.image_dir, video_stats)
			else:
				cherrylog("video already exists and has been processed.  The video should be removed from this folder. Skipping")
				continue
				#The below code can replace the above 2 lines when doing testing
				#cherrylog ("video already exists and has been processed.  But running again, for fun")
				#video_stats = vp.splice_video_into_images (self.videoInputPath,i,self.videoOutputPath, self.video_dir, self.image_dir, self.report_dir)
				#if (video_stats == None):
				#	continue
			
			#full_path_to_image_files = "./imagetaggerlib/video_process/" + self.videoOutputPath.split('/')[-1] + "/" + video.attributes['hashstring'] + "/" + self.image_dir
			full_path_to_image_files = self.videoOutputPath + "/" + video.attributes['hashstring'] + "/" + self.image_dir
			#This will create scenes in mongo for this video!
			cherrylog("Running scene processing on new video")
			scenes = sp.doProcess(video, full_path_to_image_files, "png")
			cherrylog("Running function to identify and submit a good subset of images for this video")
			vp.keep_best_destroy_rest(video, full_path_to_image_files, "png", testRun=False)
			video.update({'status':{'imagetagger_status':'processed'}}, commit=True)
				
		
	def poll_video_analysis_complete(self):
		cherrylog ("Running: poll_video_analysis_complete")
		mv.MVideo.video_analysis_complete()

	def start_timed_process(self,**kwargs):
		count = 0
		function_name = str(kwargs['called_function'].__name__)
		repeat_time = self.get_repeat_time(function_name)
		time.sleep(self.timed_processes_shutdown_time)
		while (self.running):
			if (count % self.print_timed_process_update == 0):
				cherrylog("Checking timed process: " + str(function_name) + " Current time: " + str(count) + " and interval timer: " + str(repeat_time))
			if (count >= repeat_time):
				count = 0
				kwargs['called_function']()
			else:
				count += self.timed_processes_shutdown_time
			time.sleep(self.timed_processes_shutdown_time)

	def get_repeat_time(self, function_name):
		"""docstring for get_repeat_time"""
		if (function_name == "check_for_new_videos"):
			return (int(c.configs['imagetagger']['video_process_repeat_timer_seconds']))
		elif (function_name == "poll_video_analysis_complete"):
			return (int(c.configs['imagetagger']['video_analysis_complete_timer_seconds']))
		else: return (30)
			
	def stop_timer(self):
		self.running = False
		
	@staticmethod
	def stop_timers():
		for p in TimedProcesses.registered_processes:
			p.stop_timer()