#
# datr
# Download image sets from flickr -> create your own training set for machine learning tasks etc.
# 
# Peer David (2016)
# https://github.com/peerdavid/datr
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


def parse_cmd_args():
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
    parser.add_option("-n", "--num_images", dest="max_num_img", action="store", type="int",
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
    return options

#
# Remove all files in download folder and create it if it does not exist
#  
def init_download_folder(options):
    os.popen('rm -r ' + options.path)
    os.popen('mkdir ' + options.path)
    
    
#
# Init threads which will download our images
#
def init_downloader_threads(worker_queue, options):
    print "Starting {0} downloader threads".format(options.num_threads)
    for i in range(options.num_threads):
        worker = Thread(target=download_image, args=(worker_queue, options))
        worker.setDaemon(True)
        worker.start()
        
        
#
# Download images from queue until prog. finished
#
failed_img = 0
def download_image(worker_queue, options):
    while True:
        try:
            img = worker_queue.get()
            urllib.urlretrieve(img.url_s, options.path + "/" + img.id+ ".jpg")
            save_print("Downloaded image {0}/{1}.jpg | Title = '{2}' | License = {3}".format(options.path, img.id, img.title, img.license))
        except Exception, e:
            failed_img += 1
            sys.stderr.write("Could not download image {0}/{1}.jpg | {2}".format(options.path, img.id, e))
        finally:
            worker_queue.task_done()   
            
            
def save_print(content):
    print "{0}\n".format(content),
   
    
def fill_worker_queue_with_images(worker_queue, options):
    print "Downloading images for search tags {0} and license {1}.\n".format(options.search_tags, options.license)
    walker = Walker(f.Photo.search, tags=options.search_tags, tag_mode='all', extras='url_s', license=options.license, sort='interestingness-desc')
    
    # Insert all images into worker queue
    # Note: Loop finished if no more images on flickr or > max_num_img
    num_img = 0
    for img in walker:       
        if num_img >= options.max_num_img:
            break;
        worker_queue.put(img)
        num_img += 1
        
    return num_img
        
        
def wait_for_downloader_threads(worker_queue):
    worker_queue.join()
        
        
#
# MAIN
#    
try :
    start_time = time.time()

    # Init
    options = parse_cmd_args()
    worker_queue = Queue(options.max_num_img + 1)
    init_download_folder(options)
    init_downloader_threads(worker_queue, options)

    # Fill and wait for queue
    num_img = fill_worker_queue_with_images(worker_queue, options)   
    wait_for_downloader_threads(worker_queue)

    # Print result
    end_time = time.time()
    print ""
    if num_img < options.max_num_img:
        print "There are not {0} images available.".format(options.max_num_img)
    print "Finished image download after {0:.2f} sec.".format(end_time - start_time)
    print "Successfully downloaded {0} images. Failed {1} image downloads.\n".format(num_img - failed_img, failed_img)   
       
except SystemExit:
    print ""
    
except Exception, e:
    sys.stderr.write("An unexpected error occured: {0}".format(e))