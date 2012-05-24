#!/usr/bin/env python

# This is part of the ImageTagger Backend System
#
# Author::    Jesse Smith  (mailto:jesse@steelcorelabs.com)
# Copyright:: Copyright (c) 2012 ImageTagger
import yaml, os
import cherrypy
from cherrypy import log as cherrylog

DEFAULT_ENV = 'development'
cherrypy.log ("setting up config data")
config_files = ['imagetagger','iqengines','crowdflower','cherrypy']
configs = {}

def set_env_configs(config_dir):
	try:
		configs['environment'] = str(yaml.load(open(config_dir + '/environment.yml')))
		cherrylog ("Current Environment = " + configs['environment'])
	except:
		cherrylog ("Couldn't load environment file.  Using default of " + DEFAULT_ENV)
		configs['environment'] = DEFAULT_ENV
	
	for i in config_files:
		configs[i] = yaml.load(open(config_dir + "/" +  i + '.yml'))[configs['environment']]


def set_env(env):
	for i in config_files:
		if (i == 'environment'):
			pass
		else:
			configs[i] = yaml.load(open(config_dir + "/" + i + '.yml'))[env]
	