To run: python ImageTagger.py


ImageTaggerBackend architecture:
imagetaggerlib: Contains video processing, crowdsource
processing and image/scene/video analysis.
config: contains .yml files for imagetagger and crowd sources

imagetaggerlib
---------
/media/: code to process image/scene/video.
/media_process_sources/:
/video_process/: code to split a video into images
and scene detection algorithm.


video_process
-------------
/processedVideos/: contains processed videos
/test/: contains a test video to improve on scene
detection algorithm.
/videos/: videos to be analyzed
sceneDetection.py: scene detection algorithm

media
-----
m_image.py: processes the image keyword/category
m_scene.py: processes the scene keyword/category
m_video.py: processes the video keyword/category

setup
-----
git clone git@github.com:jesses16/ImageTaggerBackend.git
mkdir imagetaggerlib/video_process/videos

Download and install python 2.7.2
mkdir ~/python/ 
./configure --prefix=/home/ubuntu/python/
make
make install

Add to ~/.bashrc
#Include Python 2.7 in path
export PATH=/home/ubuntu/python/bin:$PATH
add '/home/ubuntu/python/bin
' to /etc/environment

sudo su
sh setuptools-0.6c11-py2.7.egg
exit

sudo easy_install virtualenv
mkdir ~/python_envs
virtualenv -p python/bin/python2.7 ~/python_envs/ImageTaggerBackend
source ~/python_envs/ImageTaggerBackend/bin/activate
#undo with deactivate

For help, see: http://simononsoftware.com/virtualenv-tutorial/

cd /home/ubuntu/python/lib/python2.7/site-packages
sudo chown ubuntu:ubuntu *
easy_install yolk
yolk -l

in ~/.bashrc export PYTHONPATH=.:/home/ubuntu/.local/lib/python2.7/site-packages/:/home/ubuntu/python/lib/python2.7/site-packages/

easy_install cherrypy
easy_install pymongo
#easy_install nltk #Not currently used
run python interpreter
#nltk.download() #Not currently used
#download all-corpora #Not currently used
easy_install pyyaml
#sudo apt-get install python-numpy
#sudo apt-get install python-scipy
upload numpy / scipy sources

#Reference http://www.mongodb.org/display/DOCS/Ubuntu+and+Debian+packages
add 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' to /etc/apt/sources.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
sudo apt-get update
sudo apt-get install mongodb-10gen


sudo apt-get install liblapack-dev
#Reference http://www.scipy.org/Installing_SciPy/Linux#head-fb320be917b02f8fbe70e3fb2c9fe6f5f5f06fc2
cd into numpy directory
python setup.py install --user   # installs to your home directory -- requires Python >= 2.6

sudo apt-get build-dep python-matplotlib
cd matplotlib directory
python setup.py install --user

cd into scipy directory
sudo apt-get install gfortran
python setup.py install --user

sudo apt-get install xfsprogs xfsdump

#production is currently using the local disk space that comes with it, and thus doesn't have an sdg
#Create a new EBS for images and for mongodb
sudo mkfs -t xfs /dev/sdm
sudo mkfs -t xfs /dev/sdg
sudo mount /dev/sdm /mongodb -t xfs -o noatime,noexec,nodiratime
sudo mount /dev/sdg /home/ubuntu/www/ImageTaggerBackend/imagetaggerlib/video_process/processedVideos/ -t xfs
echo "/dev/sdm /mongodb xfs noatime,noexec,nodiratime 0 0" | sudo tee -a /etc/fstab
echo "/dev/sdg /home/ubuntu/www/ImageTaggerBackend/imagetaggerlib/video_process/processedVideos/ xfs noatime 0 0" | sudo tee -a /etc/fstab


sudo vi /etc/mongodb.conf
dbpath=/mongodb


#Start mongo with:
sudo mongod --config /etc/mongodb.conf  &

#in mongo
use BetterKeyword
db.cloneDatabase("SourceServerIP where 27017 is open");

