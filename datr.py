#
# datr
# Download image sets from flickr -> create your own training set for machine learning tasks etc.
# 
# Peer David (2016)
# https://github.com/peerdavid/datr
#

import sys
import os
import flickr_api
from flickr_api import Walker
import urllib
from Queue import Queue
from threading import Thread
from optparse import OptionParser
import time
import datetime
import ConfigParser


def _parse_cmd_args():
    parser = OptionParser()
    parser.add_option("-s", "--search_tags", dest="search_tags", action="store",
                    help="A comma-delimited list of tags. Photos with one or more" +
                        "of the tags listed will be returned. You can exclude " +
                        "results that match a term by prepending it" +
                        "with a - character.")
    parser.add_option("-f", "--use-free-text", dest="use_free_text", action="store_true",
                    help="Use free text search, if not enough images are available")
    parser.add_option("-t", "--num_threads", dest="num_threads", action="store", type="int",
                    help="Number of downloader threads (speed up download)", default=20)
    parser.add_option("-p", "--path", dest="path", action="store",
                    help="Path where downloaded files should be saved", default="download")
    parser.add_option("-n", "--num_images", dest="max_num_img", action="store", type="int",
                    help="Max. number of images to download", default=100)
    parser.add_option("-i", "--image_size", dest="image_size", action="store", default="s",
                    help="Size of images. \n" +
                         "s=Small, " + 
                         "m=Medium, " + 
                         "l=Large")
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

    if not os.path.exists(path):
        os.popen('mkdir ' + path)
    
    
def _init_downloader_threads(worker_queue, path, image_size, num_threads):
    """ Init threads which will download our images
    """
    print "Starting {0} downloader threads".format(num_threads)
    for i in range(num_threads):
        worker = Thread(target=_download_image, args=(worker_queue, path, image_size))
        worker.setDaemon(True)
        worker.start()
        
        
def _download_image(worker_queue, path, image_size):
    """  Download images from queue. Executed by one single thread.
    """
    while True:
        try:
            img = worker_queue.get()
            file_name = "{0}/{1}_{2}.jpg".format(path, img.id, img.server)
            urllib.urlretrieve(img["url_"+image_size], file_name)
            _save_print("Downloaded image {0} with license = {1}".format(file_name, img.license))
        except Exception, e:
            sys.stderr.write("ERROR | Could not download image {0} | {1} \n".format(file_name, e))
        finally:
            worker_queue.task_done()   
            
            
def _save_print(content):
    print "{0}\n".format(content),
   
    
def _fill_worker_queue_with_tagged_images(worker_queue, search_tags, license, max_num_img, image_size):
    print "Downloading images for search tags {0} and license {1}.".format(search_tags, license)

    # We read images year by year
    # https://stackoverflow.com/questions/1994037/flickr-api-returning-duplicate-photos
    now = datetime.datetime.now()
    num_img = 0
    already_exists = []
    
    for year in range(1980, now.year):
        min_upload_date = "{0}-01-01".format(year)
        max_upload_date = "{0}-01-01".format(year+1)

        walker = Walker(flickr_api.Photo.search, tags=search_tags, tag_mode='all', extras='url_'+image_size, 
            license=license, sort='relevance', min_upload_date=min_upload_date, max_upload_date=max_upload_date)
        
        # Insert all images into worker queue
        # Note: Loop finished if no more images on flickr or > max_num_img
        for img in walker:       
            if num_img >= max_num_img:
                break;

            img_id = "{0}_{1}".format(img.id, img.server)
            if(img_id not in already_exists):
                worker_queue.put(img)
                already_exists.append(img_id)
                num_img += 1
                sys.stdout.write("  Searching for images on flickr ... %d%%\r" % (num_img * 100 / max_num_img))
                sys.stdout.flush()
    print "Filled downloader queue with {0} tagged images.                        \n".format(num_img)
    return num_img


def _fill_worker_queue_with_free_text_images(worker_queue, search_text, license, max_num_img, image_size):
    print "Downloading images for free text {0} and license {1}.".format(search_text, license)
    walker = Walker(flickr_api.Photo.search, text=search_text, tag_mode='all', extras='url_'+image_size, license=license, sort='relevance')
    
    # Insert all images into worker queue
    # Note: Loop finished if no more images on flickr or > max_num_img
    num_img = 0
    for img in walker:       
        if num_img >= max_num_img:
            break;
        worker_queue.put(img)
        num_img += 1
    
    print "Filled downloader queue with {0} free text images.\n".format(num_img)
    return num_img


def _authenticate():
    print "Authenticate on flickr."
    """
    Load secret and key from home dir and authenticate at flickr
    """
    try:
        cfg = ConfigParser.RawConfigParser()
        cfg.read(os.path.expanduser('~/.datr'))       # Read file

        api_key = cfg.get("Settings", "API_KEY")
        api_secret = cfg.get("Settings", "API_SECRET")

    except:
        print "Could not find config file '~/.datr' with API_KEY and API_SECRET"
        return

    flickr_api.set_keys(api_key, api_secret)


def download(path, search_tags, use_free_text=False, license="", max_num_img=100, num_threads=15, image_size="s"):
    """ Download images from flickr. Needs a flickr_keys.py file in your execution path.

    Args:
        path: Download all images into this path
        search_tags: Search for images in flick, which are tagged with the given, comma-delimited list, of tags
        use_free_text: Use free text search, if not enough images are available
        license: Download only images of given type.
        max_num_img: Max. number of images to download
        num_threads: Number of downloader threads
    Returns:
        Number of downloaded images
    """
    num_img = 0
    try :
        print "\n#############################################"
        _authenticate()

        worker_queue = Queue(max_num_img + 1)

        # Fill and wait for queue
        start_time = time.time()
        num_img = _fill_worker_queue_with_tagged_images(worker_queue, search_tags, license, max_num_img, image_size)  

        # If there are not enough tagged img, use free text to download
        if use_free_text and num_img < max_num_img: 
            num_img += _fill_worker_queue_with_free_text_images(worker_queue, search_tags, license, max_num_img - num_img, image_size)
        
        print "#############################################\n"

        # Start all downloader threads
        _init_download_folder(path)
        _init_downloader_threads(worker_queue, path, image_size, num_threads)

        # Wait until all images downloaded
        worker_queue.join()
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
def main():
    # Run datr with cmd options
    options = _parse_cmd_args()
    download(
        options.path,
        options.search_tags,
        options.use_free_text,
        options.license,
        options.max_num_img,
        options.num_threads,
        options.image_size
    )


if __name__ == '__main__':
    main()