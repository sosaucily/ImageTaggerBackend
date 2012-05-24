
'''
Name: Frame Difference Analyzer
Date: 20.04.2009
Author: alex arsenovic
Modified by: Dmitri Skjorshammer
Date: 11/30/11
Runtime: 16 seconds for a 22 second video

Summary: 
        General frame difference analyzer. This is not a functional tool, it is made for visuallizing and 
        understanding motion detection/scene detection/ anything related to frame differencing. 
        This code is not optimized for speed in anyway. 

What it does: 
        Calculates frame differences  between sequential frames in a series of images. 
        large changes are found by calculating a rolling averate of the frame differences, and any frame 
        difference beyond a user-configured number of standarddeviations is considered a scene change. 
        The output is broken up into 2 parts: realtime output, and      post processing.   

Requirements:
        version in bracket is what i have tested it on.
        python (2.5.2-16)
        scipy (0.6.0-12)


Comparing Alex Arsenovic's and my algorithm:
        Alex uses a 200-frame rolling average similar to Bollinger Bands. I didn't like that since the 200-frame
        choice is arbitrary and ignores the _content_ of the last 200 scenes. Instead, I wanted to reset the mean
        and st. dev. after a scene change so that the mean and st.dev. are calculated _for a particular scene_.
        I ran Alex's algorithm with numStdDev = 2.5 and saved that algorithm in scene_detection_bollinger.py. It
        detected the following frames where a scene changed:
        [1, 75, 91, 166, 271, 311, 325, 398, 481, 532, 676]

        On the other hand, my algorithm was run with numStdDev = 2 and is saved in this file, scene_detection.py.
        It detected the following frames:
        {'motionIndexVector': [0, 66, 160, 175, 248, 265, 303, 377, 436, 450, 500, 634], 'num_frames': 636}

        Thus, I'm going to do with my implementation.
'''

''' 
Another scene detection algorithm which makes use Color Histogram:
http://stackoverflow.com/questions/4801053/video-scene-detection-implementation
'''
 
import glob
import numpy
#Note: pylab.imread computes image strength from 0 to 1
# while scipy.ndimage.imread computes image strength from 0 to 255; we want from 0 to 1
import pylab
import os


	    
# load initial frame, use this to initialize the imshow, might be done better
def rgb2gray(im):
    return ((im[:,:,0]+im[:,:,1]+im[:,:,2])/3)


# Purpose: Calculates the indeces where motion is detected.
# Input:
#       The full_image_dir is of the form C:/your/directory/where/images/are
#       extension is the extension of the images
#       show_charts shows the frame-by-frame analysis of the frames.
# Note:
def detect(full_image_path = './test', extension = 'png'):
    # Load the image files
    files = glob.glob(full_image_path + '/*.' + extension)
    files.sort()
    print ("current dir is " + str(os.curdir))
    print ("checking " + full_image_path + '/*' + extension + " for image files")
    print ("Found " + str(len(files)) + " files")

    if len(files) < 10:
        print "There are less than 10 images in " + str(full_image_path)

    # Initialize variables
    im = rgb2gray(pylab.imread(files[0]))
    changeVector = [0] # Holds the difference between two consecutive frames
    indexVector = [0] # Holds
    motionIndexVector=[0] # holds frame numbers which where detected as scene changes
    index = 1
    min_scene_length = 15    # minimum length of scene, in frames
    numStdDev = 5

    #print "Starting the scene detection algorithm..."
    # Frame difference loop: runs until we reach the end of images.
    # This format is required for the charts to be updated in real-time.
    # Update the sequence of images
    while index < len(files):
        im0 = im
        frame = files[index]
        im = rgb2gray(pylab.imread(frame)) #Image data of the next frame
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
        indexVector.append(index)


        # for rolling statistics we can use just the bufferLength most recent
        changeBuffer = changeVector #array(changeVector) 
        changeMean = numpy.mean(changeBuffer)
        changeStdDev = numpy.std(changeBuffer)
        upperLimit = changeMean + numStdDev*changeStdDev


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
                        motionIndexVector.append(index)
                        changeVector = []

        index += 1

    #End While Loop, Add final scene to list if it is larger than min_scene_length
    else:
        if (len (changeVector) > min_scene_length):
            motionIndexVector.append(index-1)

    return {'num_frames': len(files), 'motionIndexVector': motionIndexVector}

# For testing purposes
#print detect()




