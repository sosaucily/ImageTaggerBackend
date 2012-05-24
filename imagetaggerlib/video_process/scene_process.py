from cherrypy import log as cherrylog
from imagetaggerlib import imagetagger_tools as Tools
from imagetaggerlib.media import m_scene as ms
from pymongo import Connection
from imagetaggerlib.video_process import scene_detection

# Runs the scene detection algorithm and creates scene objects in mongo
def doProcess(video,full_path,extension):
	# Run the scene detection algorithm
	cherrylog ("Running the scene detection algorithm with video: " + str(video.attributes['friendly_id']) + " and at folder: " + str(full_path) + " with file extension: " + str(extension))
	detection_results = scene_detection.detect(full_path, extension)

	all_scenes = get_scene_stats(video.attributes['friendly_id'], detection_results['motionIndexVector'], video.attributes['fps'])
	
	cherrylog ("Done running get_scene_stats, updating video obj in database")
	# This adds the scenes to Mongo
	mongo_connection = Connection()
	bettermedia = mongo_connection['BetterMedia']
	scene_collection = bettermedia.scene
	for scene in all_scenes:
		new_scene = ms.MScene(collection=scene_collection)
		new_scene.attributes = scene
		new_scene.create()
	mongo_connection.disconnect()

## BUG BUG: write a function that returns the time in the video of any given frame.
# BUG BUG, this may be wrong since the frame rate isn't consistent
def time_of_frame_raw(index, fps):
	return ((1.0 / fps) * index)


def time_of_frame(time_seconds):
	minutes = int(time_seconds) / 60
	seconds = int(time_seconds) % 60
	milliseconds = (time_seconds - int(time_seconds) ) * 1000
	return (str(minutes) + ":" + str(seconds) + ":" + str(milliseconds))


# Returns an array of scenes with stats about the scenes.
def get_scene_stats(video_id, motionIndexVector,fps):
	cherrylog ("Running get_scene_stats")
	all_scenes = []
	try:
		for i in range(len(motionIndexVector)-1):
			num_images = motionIndexVector[i+1] - motionIndexVector[i]
			start_time = time_of_frame_raw(motionIndexVector[i], fps)
			stop_time = time_of_frame_raw(motionIndexVector[i+1], fps)
			length = time_of_frame(start_time - stop_time)

			scene = {'video': int(video_id),'scene_id': int(i),
					'start_time':float(start_time),'stop_time':float(stop_time),
					'num_images':int(num_images),'length':str(length),
					'status':{'processed':True}}

			all_scenes.append(scene)
	except Exception as e:
		Tools.print_errors ("Error running get_scene_stats on video_id: " + str(video_id))

	return all_scenes

#doProcess(1,os.curdir + '/test','png')
