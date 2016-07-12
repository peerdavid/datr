#
# datr
# Download data sets from flickr
# See also https://github.com/peerdavid/datr
#
# ToDo 
# - Select download folder for multiple downloads
# - Download images in different threads for performance improvements
#
import sys
import os
import flickr_api as f
from flickr_api import Walker
import urllib
from Queue import Queue
from threading import Thread
from optparse import OptionParser
import time


#
# Remove all files in download folder and create it if it does not exist
#  
def prepare_download_folder(path):
    os.popen('rm -r ' + path)
    os.popen('mkdir ' + path)
    
    
#
# Init all downloader threads with worker queue and download path
#
def init_downloader_threads(worker_queue, path, num_threads):
    print "Starting {0} downloader threads".format(num_threads)
    for i in range(num_threads):
        worker = Thread(target=download_image, args=(worker_queue, path))
        worker.setDaemon(True)
        worker.start()
        
        
#
# Print line per line also with multithreading
#
def safe_print(content):
    print "{0}\n".format(content),
    
    
#
# Download given images from queue q
#
def download_image(worker_queue, path):
    while True:
        try:
            photo = worker_queue.get()
            urllib.urlretrieve(photo.url_s, path + "/" + photo.id+ ".jpg")
            safe_print ("Downloaded image {0}/{1}.jpg | Title = '{2}' | License = {3}".format(path, photo.id, photo.title, photo.license))
        except:
            safe_print ("(ERROR) Could not download image {0}/{1}.jpg".format(path, photo.id))
        
        worker_queue.task_done()   

    
#
# MAIN
#    
try :
    start_time = time.time()

    # Set cmd args
    parser = OptionParser()
    parser.add_option("-s", "--search_tags", dest="search_tags", action="store",
                    help="A comma-delimited list of tags. Photos with one or more" +
                        "of the tags listed will be returned. You can exclude " +
                        "results that match a term by prepending it" +
                        "with a - character.")
    parser.add_option("-t", "--num_threads", dest="num_threads", action="store", type="int",
                    help="Number of downloader threads (speed up download)", default=20)
    parser.add_option("-p", "--path", dest="path", action="store",
                    help="Path where downloaded files should be saved", default="download")
    parser.add_option("-n", "--num_images", dest="num_img", action="store", type="int",
                    help="Max. number of images to download", default=100)
    parser.add_option("-l", "--license", dest="license", action="store", default="",
                    help="License of images.\n" +
                            "0=All Rights Reserved, " + 
                            "4=Attribution License, " + 
                            "6=Attribution-NoDerivs License, " + 
                            "3=Attribution-NonCommercial-NoDerivs License, " + 
                            "2=Attribution-NonCommercial License, " + 
                            "1=Attribution-NonCommercial-ShareAlike License, " + 
                            "5=Attribution-ShareAlike License, " + 
                            "7=No known copyright restrictions, " + 
                            "8=United States Government Work, " + 
                            "9=Public Domain Dedication (CC0) " + 
                            "10=Public Domain Mark ")
                    
    (options, args) = parser.parse_args()

    # Initialization
    worker_queue = Queue()
    init_downloader_threads(worker_queue, options.path, options.num_threads)
    prepare_download_folder(options.path)

    # Put images into worker queue for download
    print "Downloading images for search tags {0} and license {1}.\n".format(options.search_tags, options.license)
    walker = Walker(f.Photo.search, tags=options.search_tags, tag_mode='all', extras='url_s', license=options.license, sort='interestingness-desc')
    for i in range(options.num_img):
        photo = walker.next()
        worker_queue.put(photo)
   
    # Wait until queue is empty
    worker_queue.join()
    end_time = time.time()
    print "\nFinished image download after {0:.2f} sec.".format(end_time - start_time)
    
except StopIteration:
    end_time = time.time()
    print "\nThere are not " + str(options.num_img) + " " + options.search_tags + " images available."
    print "\nFinished image download after {0:.2f} sec.".format(end_time - start_time)
    
except SystemExit:
    print ""
    
except:
    print "(ERROR) An unexpected error occured:", sys.exc_info()[0]