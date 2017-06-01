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



def download(path, search_tags, license="", max_num_img=100, num_threads=15, image_size="s"):
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
    start_time = time.time()
    
    try :
        # Initialize and fill queue
        print "\n#############################################"
        _authenticate()

        worker_queue = Queue(max_num_img + 1)
        num_img = _fill_worker_queue(worker_queue, search_tags, license, max_num_img, image_size)  
        print "#############################################"

        # Start all downloader threads
        _init_download_folder(path)
        _init_downloader_threads(worker_queue, path, image_size, num_threads, max_num_img)

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


def _authenticate():
    """
    Load secret and key from home dir and authenticate at flickr
    """
    
    print "Authenticate user on flickr."
    try:
        cfg = ConfigParser.RawConfigParser()
        cfg.read(os.path.expanduser('~/.datr'))       # Read file

        api_key = cfg.get("Settings", "API_KEY")
        api_secret = cfg.get("Settings", "API_SECRET")

    except:
        print "Could not find config file '~/.datr' with API_KEY and API_SECRET"
        return

    flickr_api.set_keys(api_key, api_secret)


def _fill_worker_queue(worker_queue, search_tags, license, max_num_img, image_size):
    """
    Fill queue with images on flickr
    Note: The flickr api returns the same id, if the number of search results > 4000.
    Therefore we search for every year. \sa https://stackoverflow.com/questions/1994037/flickr-api-returning-duplicate-photos
    """
    print "Downloading images for search tags '{0}' and license '{1}'.".format(search_tags, license)

    now = datetime.datetime.now()
    num_img = 0
    already_added = []
    
    for year in range(2000, now.year):
        if num_img >= max_num_img:
                break

        min_upload_date = "{0}-01-01".format(year)
        max_upload_date = "{0}-01-01".format(year+1)

        walker = Walker(flickr_api.Photo.search, tags=search_tags, tag_mode='all', extras='url_'+image_size, 
            license=license, sort='relevance', min_upload_date=min_upload_date, max_upload_date=max_upload_date)
        
        # Insert all images into worker queue
        # Note: Loop finished if no more images on flickr or > max_num_img
        for img in walker:       
            if num_img >= max_num_img:
                break

            img_id = "{0}_{1}".format(img.id, img.server)
            if(img_id not in already_added):
                worker_queue.put(img)
                already_added.append(img_id)

                num_img += 1
                sys.stdout.write("  Searching on flickr for images ... %d%%\r" % (num_img * 100 / max_num_img))
                sys.stdout.flush()

    print "Filled downloader queue with {0} tagged images.                        \n".format(num_img)
    return num_img


def _init_download_folder(path):
    """ Remove all files in download folder and create it if it does not exist
    """

    if not os.path.exists(path):
        os.popen('mkdir ' + path)
    
    
def _init_downloader_threads(worker_queue, path, image_size, num_threads, max_num_img):
    """ Init threads which will download our images
    """
    print "Starting {0} downloader threads".format(num_threads)
    for i in range(num_threads):
        worker = Thread(target=_download_image, args=(worker_queue, path, image_size, max_num_img))
        worker.setDaemon(True)
        worker.start()
        
        
def _download_image(worker_queue, path, image_size, max_num_img):
    """  Download images from queue. Executed by one single thread.
    """
    while True:
        try:
            img = worker_queue.get()
            file_name = "{0}/{1}_{2}.jpg".format(path, img.id, img.server)
            urllib.urlretrieve(img["url_"+image_size], file_name)

            sys.stdout.write("  Downloading images ... %d%%\r" % (100 - (worker_queue.qsize() * 100 / max_num_img)))
            sys.stdout.flush()

        except Exception, e:
            sys.stderr.write("ERROR | Could not download image {0} | {1} \n".format(file_name, e))

        finally:
            worker_queue.task_done()   


#
# MAIN
#  
def main():
    # Run datr with cmd options
    options = _parse_cmd_args()
    download(
        options.path,
        options.search_tags,
        options.license,
        options.max_num_img,
        options.num_threads,
        options.image_size
    )


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


if __name__ == '__main__':
    main()
    