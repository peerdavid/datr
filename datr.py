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


def _parse_cmd_args():
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


def _init_download_folder(path):
    """ Remove all files in download folder and create it if it does not exist
    """
    os.popen('rm -r ' + path)
    os.popen('mkdir ' + path)
    
    
def _init_downloader_threads(worker_queue, path, num_threads):
    """ Init threads which will download our images
    """
    print "Starting {0} downloader threads".format(num_threads)
    for i in range(num_threads):
        worker = Thread(target=_download_image, args=(worker_queue, path))
        worker.setDaemon(True)
        worker.start()
        
        
def _download_image(worker_queue, path):
    """  Download images from queue. Executed by one single thread.
    """
    while True:
        try:
            img = worker_queue.get()
            urllib.urlretrieve(img.url_s, path + "/" + img.id+ ".jpg")
            _save_print("Downloaded image {0}/{1}.jpg | Title = '{2}' | License = {3}".format(path, img.id, img.title, img.license))
        except Exception, e:
            sys.stderr.write("Could not download image {0}/{1}.jpg | {2}".format(path, img.id, e))
        finally:
            worker_queue.task_done()   
            
            
def _save_print(content):
    print "{0}\n".format(content),
   
    
def _fill_worker_queue_with_images(worker_queue, search_tags, license, max_num_img):
    print "Downloading images for search tags {0} and license {1}.\n".format(search_tags, license)
    walker = Walker(f.Photo.search, tags=search_tags, tag_mode='all', extras='url_s', license=license, sort='interestingness-desc')
    
    # Insert all images into worker queue
    # Note: Loop finished if no more images on flickr or > max_num_img
    num_img = 0
    for img in walker:       
        if num_img >= max_num_img:
            break;
        worker_queue.put(img)
        num_img += 1
        
    return num_img
        
        
def _wait_for_downloader_threads(worker_queue):
    worker_queue.join()
        

def download_images_from_flickr(path, search_tags, license="", max_num_img=100, num_threads=15):
    """ Download images from flickr. Needs a flickr_keys.py file in your execution path.

    Args:
        path: Download all images into this path
        search_tags: Search for images in flick, which are tagged with the given, comma-delimited list, of tags
        license: Download only images of given type.
        max_num_img: Max. number of images to download
        num_threads: Number of downloader threads
    Returns:
        Number of downloaded images
    """
    num_img = 0
    try :
        worker_queue = Queue(max_num_img + 1)
        _init_download_folder(path)
        _init_downloader_threads(worker_queue, path, num_threads)

        # Fill and wait for queue
        start_time = time.time()
        num_img = _fill_worker_queue_with_images(worker_queue, search_tags, license, max_num_img)   
        print "Filled downloader queue with {0} images.".format(num_img)
        
        # Wait until all images downloaded
        _wait_for_downloader_threads(worker_queue)
        end_time = time.time()

        # Print result
        print "\nFinished image download after {0:.2f} sec.".format(end_time - start_time)
        print "Successfully downloaded {0} images.\n".format(num_img)   

    except SystemExit:
        print ""
        
    except Exception, e:
        sys.stderr.write("An unexpected error occured: {0}".format(e))
    
    finally:
        return num_img


#
# MAIN
#    
if __name__ == '__main__':
    options = _parse_cmd_args()
    download_images_from_flickr(
        options.path,
        options.search_tags,
        options.license,
        options.max_num_img,
        options.num_threads
    )