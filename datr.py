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


#
# Print line per line also with multithreading
#
def safe_print(content):
    print "{0}\n".format(content),
    
    
#
# Download given images from queue q
#
def download_image(worker_queue):
    while True:
        try:
            photo = worker_queue.get()
            safe_print ("Downloading image " + photo.id + ".jpg | Title = '" + photo.title + "' | License = " + photo.license)
            urllib.urlretrieve(photo.url_s, "download/" + photo.id+ ".jpg")
        except:
            safe_print ("(ERROR) Could not download image " + photo.id +".jpg")
        
        worker_queue.task_done()   
    
    
def init_downloader_threads(worker_queue):
    num_threads = 50
    for i in range(num_threads):
        worker = Thread(target=download_image, args=(worker_queue,))
        worker.setDaemon(True)
        worker.start()
        print "Created downloader thread #" + str(i)
    
    
#
# MAIN
#    
try :
    # Set cmd args
    parser = OptionParser()
    parser.add_option("-t", "--tags", dest="tags", action="store", default="test",
                    help="A comma-delimited list of tags. Photos with one or more" +
                        "of the tags listed will be returned. You can exclude " +
                        "results that match a term by prepending it" +
                        "with a - character.")
    parser.add_option("-p", "--path", dest="path", action="store",
                    help="Path where downloaded files should be saved", default="download")
    parser.add_option("-n", "--num_img", dest="num_img", action="store", type="int",
                    help="Max. number of images to download", default="100")
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
    search_tags = options.tags
    license = options.license
    num_img = options.num_img

    # Initialization
    worker_queue = Queue()
    init_downloader_threads(worker_queue)

    # Prepare downloader folder
    os.popen('rm -r download/')
    os.popen('mkdir download')

    # Put images into worker queue for download
    walker = Walker(f.Photo.search, tags=search_tags, tag_mode='all', extras='url_s', license=license, sort='interestingness-desc')
    for i in range(num_img):
        photo = walker.next()
        worker_queue.put(photo)
   
    worker_queue.join()
    print "\nDone."
    
except StopIteration:
    print "\nThere are not " + str(options.num_img) + " images available."
    print "Done."
    
except SystemExit:
    print ""
    
except:
    print "(ERROR) An unexpected error occured:", sys.exc_info()[0]