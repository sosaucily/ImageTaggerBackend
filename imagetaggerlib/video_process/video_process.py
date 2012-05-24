#!/usr/bin/env python

# This is part of the ImageTagger Video Pre_Processing system
#
# Authors::    Jesse Smith  (mailto:jesse@steelcorelabs.com.com) and Dmitri Skjorshammer
# Copyright:: Copyright (c) 2012 ImageTagger

import os, pickle, subprocess, shlex, sys, re
from cherrypy import log as cherrylog
from imagetaggerlib import imagetagger_tools as Tools
from imagetaggerlib.media import m_image as mi
from pymongo import Connection
import pylab
import glob

def get_video_info(videoInputPath, videoName, processedVideoPath, video_dir, image_dir, report_dir, thumb_dir):
	
	video_name_without_extension = videoName[0:videoName.rfind(".")]
	full_path = videoInputPath + "/" + videoName
	running_os = ""
	if (sys.platform.find("linux") >= 0):
		running_os = "linux"
	else:
		running_os = "osx"
	
	md5 = get_md5(full_path, running_os)
	
	#Create destination directories
	try:
		os.makedirs(processedVideoPath + "/" + md5)
		os.makedirs(processedVideoPath + "/" + md5 + "/" + video_dir)
		os.makedirs(processedVideoPath + "/" + md5 + "/" + image_dir)
		os.makedirs(processedVideoPath + "/" + md5 + "/" + report_dir)
		os.makedirs(processedVideoPath + "/" + md5 + "/" + thumb_dir)
	except OSError as err:
		Tools.print_errors("Error creating directories for video proprocess: " + str(videoName))
		cherrylog ("file exists, so skipping this video " + full_path)
		return None
			
	#Gathering specs for the video
	ffmpeg_info_command = "ffmpeg -i \"%s\"" % ( full_path )
	args = shlex.split (ffmpeg_info_command)

	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_value, stderr_value = p.communicate()

	video_info = repr(stderr_value)
	
	vid_res = re.search ('\d\d\d[\d]?x\d\d\d[\d]?' , video_info)
	if (vid_res != None):
		video_res = vid_res.group(0)

	if (video_res == None or video_res == ""):
		video_res = ""
	else:
		resolution = getResolution(video_res)
		
	duration_string = re.search('\d\d:\d\d:\d\d\.\d\d', video_info).group(0)
	duration = get_video_duration(duration_string)
	
	fps_query = re.search('\d\d\.\d\d fps', video_info)
	if (fps_query == None):
			fps_query = re.search('\d\d\.\d fps', video_info)
			if (fps_query == None):
				fps_query = re.search('\d\d\ fps', video_info)
	if (fps_query == None):
		fps = 0
	else:		
		fps_string = fps_query.group(0)
		fps = get_FPS(fps_string)
	
	return ({
		'hashstring':str(md5),
		'width':str(resolution["width"]),
		'height':str(resolution["height"]),
		'length':duration,
		'friendly_id': int(video_name_without_extension),
		'fps': fps
		})
	
	
def splice_video_into_images(videoInputPath, videoName, processedVideoPath, image_dir, video_stats):

	video_name_without_extension = videoName[0:videoName.rfind(".")]
	full_path = videoInputPath + "/" + videoName
	
	md5 = video_stats['hashstring']
	width = video_stats['width']
	height = video_stats['height']
	#Grab images for video
	
	#Because it seems we will always want all the frames, commenting out the ability to set FPS
	#ffmpeg_shell_command = "ffmpeg -i \"%s\" -r %s -s %s \"%s/%s/%s/image_%%06d.jpg\"" % ( videoInputPath +"/" + videoName, images_per_sec, str(resolution["width"]) + "x" + str(resolution["height"]), processedVideoPath, video_md5sum, imagesSubDir)
	
	ffmpeg_shell_command = "ffmpeg -i \"%s\" -s \"%s\" \"%s/%s/%s/image%s06d.png\"" % ( full_path, width + "x" + height, processedVideoPath, md5, image_dir, "%")
	
	cherrylog ("running ffmpeg -> " + ffmpeg_shell_command)
	#test_string = re.sub(r'\x00', '', ffmpeg_shell_command)
	#encoded_ffmpeg_command = cStringIO.StringIO(test_string)
	#cherrylog (" does it contain nulls? " + str(ffmpeg_shell_command.find('\0')))
	args = shlex.split(ffmpeg_shell_command.encode('utf-8'))
	p = subprocess.call(args)
	
	#Also build jpg files for web hosting
	ffmpeg_shell_command_jpg = "ffmpeg -i \"%s\" -s \"%s\" \"%s/%s/%s/image%s06d.jpg\"" % ( full_path, width + "x" + height, processedVideoPath, md5, image_dir, "%")
	
	cherrylog ("running ffmpeg -> " + ffmpeg_shell_command_jpg)
	
	args = shlex.split(ffmpeg_shell_command_jpg.encode('utf-8'))
	p = subprocess.call(args)

	os.remove(full_path)
	return True
	
def get_thumbnail(videoInputPath, videoName, processedVideoPath, thumb_dir, thumb_name, video_stats):
	cherrylog ("Getting thumbnail for video " + videoName)
	full_path = videoInputPath + "/" + videoName
	
	md5 = video_stats['hashstring']
	width = video_stats['width']
	height = video_stats['height']
	length_seconds = video_stats['length'] / 1000
	
	ffmpeg_shell_command = "ffmpeg -itsoffset -%d -i \"%s\" -vcodec mjpeg -vframes 1 -an -f rawvideo -s \"%s\" \"%s/%s/%s/%s\"" % ( length_seconds / 2, full_path, width + "x" + height, processedVideoPath, md5, thumb_dir, thumb_name)
	
	args = shlex.split(ffmpeg_shell_command.encode('utf-8'))
	p = subprocess.call(args)
	
	cherrylog ("running ffmpeg -> " + ffmpeg_shell_command)	
	
	return True
	
def get_FPS(video_fps):
	#should be in the format "24.97 fps"
	#But might be in format "25 fps"
	#Or "25.3 fps" ??
	return int(round(float(video_fps.split(" fps")[0])))
	
	
def get_video_duration(duration_string):
	d_elems = duration_string.split(":")
	d_hrs = int(d_elems[0])
	d_mins = int(d_elems[1])
	d_elems_sec = d_elems[len(d_elems)-1].split(".")
	d_sec = int(d_elems_sec[0])
	d_millis = int(d_elems_sec[1]) * 10
	return ((d_hrs * 60 * 60 * 1000) + (d_mins * 60 * 1000) + (d_sec * 1000) + (d_millis))
	
	
def getResolution(video_res):
	x_index = video_res.find("x")
	resolution = {"width":"", "height":""}
	if (x_index > 0):
		width = int(video_res[0:x_index])
		height = int(video_res[(x_index+1):len(video_res)])
		if (width > 640):
			ratio = float(height) / width
			width = 640
			height = int(round(640 * ratio))
		if (height > 640): #This is pretty strange, height is greater than width...
			ratio = width / height
			height = 640
			width = int (round(640 * ratio))
		resolution["width"]=width
		resolution["height"]=height
	return (resolution)
	
		
def get_md5(path, running_os):
	if (running_os == "linux"):
		md5_shell_command = "md5sum \"%s\"" % (path)
	elif (running_os == "osx"):
		md5_shell_command = "md5 \"%s\"" % (path)
	else:
		md5_shell_command = "md5sum \"%s\"" % (path)
		
	md5_args = shlex.split(md5_shell_command)
	cherrylog ("Running md5sum command: " + md5_shell_command )
	video_md5sum_b = subprocess.check_output(md5_args)
	video_md5sum_long = video_md5sum_b.decode("utf-8")
	
	video_md5sum = ""
			
	#On OS X with the md5 command, we want the last
	if (running_os == "osx"):
		intBreak = video_md5sum_long.rfind(" ")
		video_md5sum = video_md5sum_long[intBreak+1:intBreak+33]
	#On linux with the md5sum command, we want the first segment
	elif (running_os == "linux"):
		intBreak = video_md5sum_long.find(" ")
		video_md5sum = video_md5sum_long[0:intBreak]
	else:
		intBreak = video_md5sum_long.find(" ")
		video_md5sum = video_md5sum_long[0:intBreak]
	
	
	cherrylog ("Got video md5sum of " + video_md5sum)
	return video_md5sum


def is_nontrivial_image(image_file_name):
	cherrylog("checking if this image is non_trivial: " + image_file_name)
	image = pylab.imread(image_file_name)
	height = len(image)
	width = len(image[0])
	white_image_sum = 3*height*width #The max sum for an image
	if ( (image.sum() < (0.05 * white_image_sum)) or (image.sum() > (0.95 * white_image_sum))):
		cherrylog("No, it is trivial because the sum of the pixel values is: " + str(image.sum()))
		return False
	else:
		cherrylog("Yes, it is valid and non-trivial.  Pixel sum is: " + str(image.sum()))
		return True

def find_nearby_nontrivial_image(nearby_files):
	cherrylog("Running 'find_nearby_nontrivial_image' against " + str(len(nearby_files)) + " nearby files")
	num_files = len(nearby_files)
	check = int(num_files/2)
	count = 1
	while (check >= 0 and check < num_files):
		if (is_nontrivial_image(nearby_files[check])):
			cherrylog("Found a nontrivial nearby image at subindex: " + str(check))
			return check #Found a nearby nontrivial image, returning the index of it
		else:
			if (count % 2 == 0):
				check += count
			else:
				check -= count
		count += 1
		
	#Couldn't find a nearby nontrivial image!
	return None
	
#This function will delete off the file system all images that are unneeded.
#Files that are remaining will be created in mongo as MImage objects
def keep_best_destroy_rest(video, image_path, image_file_extention, testRun=False):
	files = glob.glob(image_path + '/*.' + image_file_extention)
	files.sort()
	cherrylog("Number of image files found for this video: " + str(len(files)) + " files.")
	video_friendly_id = video.attributes['friendly_id']
	video_fps = video.attributes['fps']
	keep_images = []
	#delete_images = [0]*(local_range*2) #List of pre-allocated size
	
	#Loop through the images files, keep the good one per fps, delete the rest
	for image_count in range(len(files)):
		sub_count = 0
		local_range = 5
		
		#Don't include the very first frame of the video
		if (image_count < local_range):
			cherrylog("Skipping first few image files")
			cherrylog("deleting file " + str(files[image_count]))
			os.remove(files[image_count])
			os.remove(files[image_count][0:-4] + ".jpg")
			continue
			
		#if the current count is fps-local_range (AKA: the beginning of the range to check)...
		if ( (image_count % video_fps) == (video_fps - local_range) ):
			cherrylog("Checking image: " + str(files[image_count]))
			
			#We're at the end of the files, so send the rest
			if (len(files) < (image_count + local_range*2)):
				local_image_list = files[image_count:len(files)-1]
				cherrylog ("Grabbing the rest of the image list")
				
			#Grab the array of the current file, plus the next range*2
			#The center of this new array is the item we are going to start with
			else:
				local_image_list = files[image_count:image_count+(local_range*2)]
				
			subindex = find_nearby_nontrivial_image(local_image_list)
			if (subindex != None):
				keep_images.append({(int(round((image_count+local_range)/video_fps))):local_image_list[subindex]})
			else:
				cherrylog ("Couldn't find a non-trivial image near image: " + str(files[image_count]))
				
			#Delete the items that weren't chosen from the local_image list.
			#If subindex is None, this will delete that whole list.
			for item in range(len(local_image_list)):
				if (item != subindex):
					cherrylog("deleting file " + str(local_image_list[item]))
					os.remove(files[image_count + item]) #Delete unneeded images
					os.remove(files[image_count + item][0:-4] + ".jpg")
		elif ( (image_count % video_fps < (video_fps - local_range)) and (image_count % video_fps >= local_range) ):
			cherrylog("deleting file " + str(files[image_count]))
			os.remove(files[image_count]) #Delete unneeded images
			os.remove(files[image_count][0:-4] + ".jpg")
			#these should delete at the end
		else:
			pass
			
	mongo_connection = Connection() #This gets closed by the parent destructor
	bettermedia = mongo_connection['BetterMedia']  # `BetterMedia` database
	image_collection = bettermedia.image  # `image` collection
	
	for k_image in keep_images:
		new_image = mi.MImage(collection=image_collection)
		cherrylog("creating image with time and filename values of : " + str(k_image))
		image_filename_png = (k_image.values()[0]).split("/")[-1]
		image_filename_jpg = image_filename_png[0:-4] + ".jpg"
		new_image.attributes = {
			'video':video_friendly_id,
			'time_in_video':k_image.keys()[0],
			'filename':image_filename_jpg
			}
		if (not testRun):
			new_image.create()

#This function sets the MImages for this video to "{'send_to_crowd':True}" 
#depending on the type of process.  "premium" = 1 per 2 sec, "basic" = 1 per 4 sec
def get_images_for_processing(video_id, quality):
	pass
	
# The full_image_path is of the form C:\your\directory\where\images\are
def delete_trivial_images(full_image_path,extension = 'png'):
        # This matches all files whose extension is 'extension' in the
        # full_image_path
        files = glob.glob(full_image_path + '/*.' + extension)
        files.sort()
        print "Number of files found: " + str(len(files)) + " files."

        num_deleted = 0
        for file_name in files:
                image = pylab.imread(file_name)
                height = len(image)
                width = len(image[0])
                white_image_sum = 3*height*width #The max sum for an image
                if image.sum() < 0.05 * white_image_sum or image.sum() > 0.95 * white_image_sum:
                        #delete file_name because it's too dark or too bright
                        os.remove(full_image_path + '/' + file_name)
                        num_deleted += 1
        print "Deleted " + str(num_deleted) + " files."


# This runs through the images and identifies those images that are duplicates.
# This returns the set of images that are 'unique' and can be sent to the Crowd.
# BUG BUG: I have similar code in scene_detection.py which means we run through
# the images twice. Once performance starts mattering, we can do everything in a single
# run.
def rgb2gray(im):
        '''duh'''
        return ((im[:,:,0]+im[:,:,1]+im[:,:,2])/3)

def get_unique_images(full_image_path,extension='png'):
        duplicate_image_std_dev = 1
        min_scene_length = 10     # minimum length of scene, in frames

        ############# load files        ####################### 
        files = glob.glob(os.curdir + full_image_path + '/*.' + extension)
        files.sort()
        print "Number of files found: " + str(len(files)) + " files."
        

        #NOTE: ffmpeg doesn't sample always sample 1 frame so it's necessary to create the following.
        # It stores a frame number (in the file name).
        frame_numbers = []
        for file_name in files:
                reg_exp_match = re.findall('\d*',file_name)
                frame_numbers.append(int([el for el in reg_exp_match if el.isdigit()][0]))


        # load initial frame, use this to initialize the imshow, might be done better
        im = rgb2gray(pylab.imread(files[0]))
        changeFrameMax =1 # set this to max value the gray-scaled image can have. depends on 
                                                # how you convert to grayscale
        index = 0


        # Duplicate images
        dup_images = []
        category_dup_images = [] #each element is a different category of duplicate images
        dup_im_change_vector = []
        unique_images = []


        # end of movie detection, calls post processing
        while index < len(files):
                # load the frame
                frame = files[index]

                im0 = im
                im = rgb2gray(pylab.imread(frame))
                
                # calculate magnitude of frame difference 
                changeFrame = abs(im- im0)

                #changeFrame.size is number of pixels; changeFrameMax is max value
                # each pixel can take. Thus the denominator is the maximum value an image attains.
                #sum literally adds all the pixels in the frame difference.
                try:
                        change =  changeFrame.sum()/(changeFrame.size * changeFrameMax) 
                except:
                        change = 0

                ############# DUPLICATE IMAGE WORK ###############
                dup_images.append(frame_numbers[index])
                dup_im_change_vector.append(change)
                dup_image_mean = mean(array(dup_im_change_vector))
                dup_image_stdev = standard_deviation(array(dup_im_change_vector))
                dup_im_threshold = dup_image_mean + duplicate_image_std_dev * dup_image_stdev
                
                # if the change is larger than our dupl_image_std_dev, then that's a different image
                if change > dup_im_threshold:
                        print dup_images
                        #Add the set of dup_images to be a category
                        category_dup_images.append(dup_images)
                        #Choose the middle image of the set
                        unique_images.append(dup_images[int(len(dup_images)/2)])
                        
                        #Reset dup_images
                        dup_images = []
                        dup_im_change_vector = []

                
                index += 1

        return unique_images
