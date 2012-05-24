#!/usr/bin/env python

import os, sys, json
import cherrypy
from cherrypy import log as cherrylog
from datetime import datetime
import yaml
from imagetaggerlib import cherrypy_tools
from threading import Thread
import argparse

from routes import *
#from routes import keyword

cmd_folder = os.path.dirname(os.path.abspath(__file__))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

import config

from imagetaggerlib import image_analysis
from imagetaggerlib import timed_processes

if __name__ == '__main__':
	cherrylog ("starting ImageTaggerBackend")

	parser = argparse.ArgumentParser(description='Running ImageTagger Backend Process.')
	parser.add_argument('--config-file-dir', action='store', required=True, dest='config_file_dir', help='Required: config file dir')
	args = parser.parse_args()
	if (str(args.config_file_dir)[0] != '/'):
		print ("Config File Dir must be an absolute path.")
		sys.exit()
	print("Config File Dir = " + str(args.config_file_dir))
	
	config.set_env_configs(str(args.config_file_dir))
	root = root.Root()

	#add the view to the web service
	root.keyword = keyword.Keyword()
	root.video = video.Video()
	root.image = image.Image()
		
	cherrylog('Starting server: %s' %str(datetime.now()))

	processes = []
	#Set up timed processes 
	time_proc = timed_processes.TimedProcesses()
	time_proc.t = Thread(target=time_proc.start_timed_process, kwargs={'called_function':time_proc.check_for_new_videos})
	time_proc.t.start()
	processes.append(time_proc)
	
	time_proc = timed_processes.TimedProcesses()
	time_proc.t = Thread(target=time_proc.start_timed_process, kwargs={'called_function':time_proc.poll_crowd_flower_jobs})
	time_proc.t.start()
	processes.append(time_proc)
	
	time_proc = timed_processes.TimedProcesses()
	time_proc.t = Thread(target=time_proc.start_timed_process, kwargs={'called_function':time_proc.poll_video_analysis_complete})
	time_proc.t.start()
	processes.append(time_proc)
	
	#Stop thread on cherrypy shutdown
	cherrypy.engine.subscribe('exit', timed_processes.TimedProcesses.stop_timers)
	
	cherrypy.quickstart(root, '/', config=config.configs['cherrypy'])