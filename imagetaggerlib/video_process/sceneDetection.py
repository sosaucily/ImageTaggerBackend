'''
Name: Frame Difference Analyzer
Date: 20.04.2009
Author: alex arsenovic

Summary: 
	General frame difference analyzer. This is not a functional tool, it is made for visuallizing and 
	understanding motion detection/scene detection/ anything related to frame differencing. 
	This code is not optimized for speed in anyway. 

What it does: 
	Calculates frame differences  between sequential frames in a series of images. 
	large changes are found by calculating a rolling averate of the frame differences, and any frame 
	difference beyond a user-configured number of standarddeviations is considered a scene change. 
	The output is broken up into 2 parts: realtime output, and 	post processing.  
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
'''

''' 
Another scene detection algorithm which makes use Color Histogram:
http://stackoverflow.com/questions/4801053/video-scene-detection-implementation
'''

from scipy.ndimage import * 
import glob,os,time,gobject
import matplotlib
matplotlib.use('GTKAgg') # this is used for drawing
from numpy import *
from pylab import * 


# functions 
def rgb2bw(im):
	'''duh'''
	return round_((im[:,:,0]+im[:,:,1]+im[:,:,2])/3)

def rgb2gray(im):
	'''duh'''
	return ((im[:,:,0]+im[:,:,1]+im[:,:,2])/3)

def point2Gaps(a):
	''' takes a 1D vector and returns the intervales between sequential elements
	'''
	gaps = zeros(size(a)-1)
	for cnt in range(0,size(a)-1):
		gaps[cnt] = a[cnt+1] - a[cnt]
	return gaps	


################### input	####################### 
picNames = 'interview'	# spefic to my file structure see load files
dirName = '/test/'

changeBufferLength = 200 # length of rolling stats, in frames
minSceneLength = 10 	# minimum length of scene, in frames
numStdDev = 3
# output switches
realTimeSwitch = True	# shows realtime analysis along with video
postProcessingSwitch = False	# show post processing results
renderOut = False

############# load files 	####################### 
files = glob.glob(os.curdir + dirName + picNames+'*.png')
files.sort()
print "Number of frames is: "
framesPerSecond = len(files)/23.0 # Should be known from your parsing 


# load initial frame, use this to initialize the imshow, might be done better
im = rgb2gray(imread(files[0]))
changeFrameMax =1 # set this to max value the gray-scaled image can have. depends on 
					# how you convert to grayscale

############## initialize graphics 	####################### 
# create subplots for frames
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

# setup rolling average statistics visualizations
meanLine = axhline(0,linewidth=2,color='r')
stdDevSpan = axhspan(0,0,alpha=.1)


################ initial variables 	####################### 
# lists to hold frame number and sum of the frame to frame  difference, called 'change'
changeVector=[0]
# holds frame numbers
frameVector=[0]
frameNo = 0
# holds frame numbers which where detected as scene changes
motionFrameVector=[0]

# for fps calculation
tStart = time.time()
t0=tStart
colorString=['y','b','g','m','r']

# needed fro drawing
manager = get_current_fig_manager()



#################### frame difference lope	####################### 
def frameDiffLoop(*args):
	global frameNo, im, changeVector, frameVector,t0,motionFrameVector, colorString,tStop,changeFameMax
	

	# used for framerate calculation
	perSecond = time.time() - t0
	t0 = time.time()

	# load the frame
	frame = files[frameNo]
	im0 = im #Image data of the current frame
	im = rgb2gray(imread(frame)) #Image data of the next frame
	# calculate magnitude of frame difference 
	changeFrame = abs(im- im0) #Vector comparing pixel by pixel

	# hack needed because the change value from initial frame to first 
	# frame is 0. and 0/somthing = nan. could be fixed with a better init
	if changeFrame.sum() == 0: change = 0
	else: change =  changeFrame.sum()/(changeFrame.size * changeFrameMax) #changeFrame.size is number of pixels; changeFrameMax is max value
	# each pixel can take. Thus the denominator is the maximum value an image attains.
	#sum literally adds all the pixels in the frame difference.

	# update our data vectors
	changeVector.append(change)	
	frameVector.append(frameVector[-1]+1)


	######################  show realtime plot	####################### 
	thePlot[0].set_data(frameVector,changeVector)
	plotSub.set_ylim([0,max(changeVector)])
	if size(frameVector) > changeBufferLength:
		plotSub.set_xlim([frameVector[-changeBufferLength],frameVector[-1]])
	else:
		plotSub.set_xlim([0,frameVector[-1]])

	# for rolling statistics we can use just the bufferLength most recent
	changeBuffer = changeVector[-changeBufferLength:]


	#NOTE: HAD TO ADD THIS LINE TO FIX ERROR
	changeBuffer = array(changeBuffer) 
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


	# draw statistical information
	subplot(212)
	infoString = 'FPS: %01.1f, mean=%0.2f, $\sigma$= %0.2f'%(1./perSecond, changeMean,changeStdDev)
	title(infoString)


	##  show the changeFrame
	if change > upperLimit:
		# ASSERT: Motion Detected!
		ylabel('!!!!!! MOTION !!!!!!!')
		subplot(212)
		axvline(frameNo,linewidth=2,color='g')
		motionFrameVector.append(frameNo)
	else:
		ylabel('')
	
	# update with new frame data
	theShow1.set_data(changeFrame)
	theShow2.set_data(imread(frame))

	if realTimeSwitch:
		theFig.canvas.draw()

	if renderOut:
		outFile = 'out%04d'%(frameNo)
		theFig.savefig(outFile)

	# counter stuff
	frameNo += 1


	# end of movie detection, calls post processing
	if frameNo < size(files):
		return True
	else:
		tStop = time.time()
		if postProcessingSwitch:
			####################### post processing #######################
			# lengths of each scene
			sceneLengths = point2Gaps(motionFrameVector)
			# number of scenes which have length > minSceneLength
			numScenes = sum( array(point2Gaps(motionFrameVector))>minSceneLength)
			# average frame difference for entire movie
			changeTotalMean = mean(changeVector)
			# std deviange for frame difference of entire movie
			changeTotalStdDev = standard_deviation(changeVector)
		
		
	
			# histogram of scene lengths
			theFig2 = figure(2,figsize=(10,8))
			ax1 = axes([0.1, 0.3, 0.8, 0.6])
			hist(sceneLengths,bins = 100)
			title('histogram of intervals between scene changes')
			xlabel('intervals between scene changes (#frames)')
			grid(1)
		
			# timeline of scenes blocks
			ax2 = axes([0.1, 0.1, 0.8, 0.10], yticks=[0])
			xlabel('Frame Number')
			for x in range(0,size(motionFrameVector)-1):
				axvspan(motionFrameVector[x],motionFrameVector[x+1],alpha=.5, facecolor=colorString[randint(0,4)])
		
			xlim([0,frameNo])
		
			# histogram of frame differences
			theFig3 = figure(3)
			changeVectorHist = histogram(changeVector,bins= size(changeVector)/10)
			plot(changeVectorHist[1],changeVectorHist[0])
			for x in range(1,5):
				axvspan( changeTotalMean- x*changeTotalStdDev, changeTotalMean + x*changeTotalStdDev,facecolor=colorString[x],alpha=.1)
		
			xlabel('Frame Difference (sum(a-b))')
			title('Histogram of Frame Differences for entire movie')
			ylabel('Normalized Sum of Frame Difference ')
			grid(1)
			show()
		return False


################# call to frame Difference loop 	####################### 
gobject.idle_add(frameDiffLoop)
show()

def numScenes():
	return (size(motionFrameVector))

def frameStartingTime(i):
	return ((1.0 / framesPerSecond) * frameVector[i])

def sceneStartingTime(i):
	return ((1.0 / framesPerSecond) * motionFrameVector[i])

def sceneLength(i):
	if i == 0: return 0
	else: return (sceneStartingTime(i) - sceneStartingTime(i-1))

def toTime(secondsTime):
	minutes = int(secondsTime) / 60
	seconds = int(secondsTime) % 60
	return (str(minutes) + ":" + str(seconds))


print "There were " + str(len(motionFrameVector)) + " scenes."

sceneStart = []
sceneLength = []

for i in range(len(motionFrameVector)):
	print "The " + str(i) + " th scene started at " + toTime(sceneStartingTime(i))
	print " and lasted for " + toTime(sceneLength(i)) + " seconds."
	sceneStart.append(toTime(sceneStartingTime(i)))
	sceneLength.append(toTime(sceneLength(i)))
	


# terminal  output
print 'average framerate: '+repr(int(frameNo/(tStop-tStart)))
print 'number of scenes over ' + repr(minSceneLength) + ' frames: ' +repr( sum( array(point2Gaps(motionFrameVector))>minSceneLength))

print sceneStart
print sceneLength

