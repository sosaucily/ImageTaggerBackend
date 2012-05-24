
'''
Name: Frame Difference Analyzer
Date: 20.04.2009
Author: alex arsenovic
Modified by: Dmitri Skjorshammer
Date: 11/30/11

Summary: 
        General frame difference analyzer. This is not a functional tool, it is made for visuallizing and 
        understanding motion detection/scene detection/ anything related to frame differencing. 
        This code is not optimized for speed in anyway. 

What it does: 
        Calculates frame differences  between sequential frames in a series of images. 
        large changes are found by calculating a rolling averate of the frame differences, and any frame 
        difference beyond a user-configured number of standarddeviations is considered a scene change. 
        The output is broken up into 2 parts: realtime output, and      post processing.  
        - realtime output: 
                shows current frame and difference between current and previous frame.
                plots the sum of the difference, allong with rolling average, and number standarder
                deviations from mean defined by the user. 
        - post processing: 
                histogram of frame differences for entire movie, with standard deviations labeled
                histogram of length of scenes, (number of frames between scene changes)
                timeline of movie with scenes colored. 

Requirements:
        version in bracket is what i have tested it on.
        python (2.5.2-16)
        matplotlib (0.98.3-5)
        scipy (0.6.0-12)
        python-gtk (2.12.1-6)


Comparing Alex Arsenovic's and my algorithm:
        Alex uses a 200-frame rolling average similar to Bollinger Bands. I didn't like that since the 200-frame
        choice is arbitrary and ignores the _content_ of the last 200 scenes. Instead, I wanted to reset the mean
        and st. dev. after a scene change so that the mean and st.dev. are calculated _for a particular scene_.
        I ran Alex's algorithm with numStdDev = 2.5 and saved that algorithm in scene_detection_bollinger.py. It
        detected the following frames where a scene changed:
        [1, 75, 91, 166, 271, 311, 325, 398, 481, 532, 676]

        On the other hand, my algorithm was run with numStdDev = 2 and is saved in this file, scene_detection.py.
        It detected the following frames:
        [1, 74, 166, 181, 254, 271, 311, 398, 465, 481, 532, 676]

        Thus, I'm going to do with my implementation.
'''

''' 
Another scene detection algorithm which makes use Color Histogram:
http://stackoverflow.com/questions/4801053/video-scene-detection-implementation
'''

from scipy.ndimage import * 
import glob,os,time ,gobject
import matplotlib
matplotlib.use('GTKAgg') # this is used for drawing
from numpy import *
from pylab import *
import re


# Load the image files
full_image_path = os.getcwd() + '/test'
extension = 'png'
files = glob.glob(full_image_path + '/*.' + extension)
files.sort()
print 'loaded stuff from ' + full_image_path
#print files


#print imread(files[0])
#print str(len(files)) + " files loaded."

	    
# load initial frame, use this to initialize the imshow, might be done better
def rgb2gray(im):
	    '''duh'''
	    return ((im[:,:,0]+im[:,:,1]+im[:,:,2])/3)
im = rgb2gray(imread(files[0]))
#im = rgb2gray([[[1 1 1]]])

# Initialize graphics
theFig = figure(1)
showSub1 = theFig.add_subplot(221,xticks=[],yticks=[])
theShow1 = imshow(im)
gray()
title('Difference')
showSub2 = theFig.add_subplot(222,xticks=[],yticks=[])
theShow2 = imshow(im)
title('Original')
# create subplot for the frame difference plot
plotSub = theFig.add_subplot(212)
thePlot = plot([0,0],'-o')
grid(1)
xlabel('Frame Number')
meanLine = axhline(0,linewidth=2,color='r')
stdDevSpan = axhspan(0,0,alpha=.1)
colorString=['y','b','g','m','r']
manager = get_current_fig_manager() # needed for drawing


# Initialize variables
changeVector = [0] # Holds the difference between two consecutive frames
indexVector = [0] # Holds
totalVector = [0]
motionIndexVector=[0] # holds frame numbers which where detected as scene changes
index = 1
changeBufferLength = 200 # length of rolling stats, in frames
min_scene_length = 10    # minimum length of scene, in frames
numStdDev = 2
show_charts = True


# for fps calculation
tStart = time.time()
t0 = tStart



################### input  #######################
# Purpose: Calculates 
# Input:
#       The full_image_dir is of the form C:/your/directory/where/images/are
#       extension is the extension of the images
#       show_charts shows the frame-by-frame analysis of the frames.
# Note:
def main():


	

    #print "Starting the scene detection algorithm..."
    # Frame difference loop: runs until we reach the end of images.
    # This format is required for the charts to be updated in real-time.
	def frameDiffLoop(*args):
		global index, im, files, changeVector, indexVector, t0,motionIndexVector, colorString      

        # Update the sequence of images
		im0 = im
		frame = files[index]
		im = rgb2gray(imread(frame)) #Image data of the next frame
		changeFrame = abs(im- im0) #Vector comparing pixel by pixel

		#changeFrame.size is number of pixels; changeFrameMax is max value
		# each pixel can take. Thus the denominator is the maximum value an image attains.
		#sum literally adds all the pixels in the frame difference.
		try:
				change =  changeFrame.sum()/(changeFrame.size) 
		except:
				change = 0


		# update our data vectors
		changeVector.append(change)
		totalVector.append(change)
		indexVector.append(index)


		# Plot analytics
		thePlot[0].set_data(indexVector,totalVector)
		#plotSub.set_ylim([0,max(changeVector)])
		if size(indexVector) > changeBufferLength:
				plotSub.set_xlim([indexVector[-changeBufferLength],indexVector[-1]])
		else:
				plotSub.set_xlim([0,indexVector[-1]])
		# for rolling statistics we can use just the bufferLength most recent
		changeBuffer = array(changeVector) 
		changeMean = mean(changeBuffer)
		changeStdDev = standard_deviation(changeBuffer)
		upperLimit = changeMean + numStdDev*changeStdDev
		lowerLimit = changeMean - numStdDev*changeStdDev
		# draw mean line and limits
		meanLine.set_ydata(changeMean)
		stdDevSpan.set_xy(array([\
		[ 0.  ,  lowerLimit],\
		[ 0.  ,  upperLimit],\
		[ 1.  ,  upperLimit],\
		[ 1.  ,  lowerLimit],\
		[ 0.  ,  lowerLimit]]) )
		# update the plots with new data
		theShow1.set_data(changeFrame)
		theShow2.set_data(imread(frame))
		# If we want to see analytics, then draw the plots.
		if show_charts:
				theFig.canvas.draw()

		# If the change is significant, show that in the plot and reset changeVector.
		# Concern: by resetting changeVector, the initial mean and st.dev. will be high when a new scene
		# starts. This means that there has to be an unusually large diff between images close after a
		# scene change.
		# Justification: this is fine since when a viewer experiences a scene change, he must get acclimated
		# to the new scene. Thus, if there is a lot of things happening in the new scene very soon after
		# it happened (and doesn't get identified as a new scene by our algorithm), then it's fine since
		# the user doesn't have the time to process everything in those few milliseconds. Furthermore,
		# identifying an image in that chaos is futile.
		if change > upperLimit and len(changeVector) > min_scene_length:
				axvline(index,linewidth=1,color='g')
				motionIndexVector.append(index)
				changeVector = []
		else:
				ylabel('')

		index += 1

		# end of movie detection, calls post processing
		if index < size(files):
			return True
		else:
			close()
			return False



	# Calls the frame difference loop until we run out of images.
	gobject.idle_add(frameDiffLoop)
	show()
	print {'num_frames': len(files), 'motionIndexVector': motionIndexVector}
	return {'num_frames': len(files), 'motionIndexVector': motionIndexVector}
	#print "There were " + str(len(motionIndexVector)) + " scenes."
			 

if __name__ == '__main__':
    main()
else:
	print 'Scene detection algorithm loaded'





