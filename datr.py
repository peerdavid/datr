import sys
import os
import flickr_api as f
from flickr_api import Walker
import urllib

try :
    search_tags = sys.argv[1]
    num_img = int(sys.argv[2])
    
    try :
        access_token = sys.argv[3]
        f.set_auth_handler(access_token)
    except IndexError : pass
    
    print "Removing all files from directory download/"
    os.popen('rm -r download/')
    os.popen('mkdir download')
    
    print "Downloading images for " + search_tags

    # tag_mode (Optional)
    # Either 'any' for an OR combination of tags, or 'all' for an AND combination. Defaults to 'any' if not specified.
    w = Walker(f.Photo.search, tags=search_tags, tag_mode='all', extras='url_s', sort='interestingness-desc')
    i = 0
    for photo in w:
        i += 1
        if i > num_img:
            break
        print "Downloading image " + photo.title
        urllib.urlretrieve(photo.url_s, "download/image-" + str(i) + ".jpg")
   
    print "\nDone. \nDownloaded " + str(i) + " images. \n"
         
except IndexError :
    print ""
    print "Usage: python datr.py [tags] [num] [access_token_file]"
    print "Download a data set from flickr for given tags. All tags will be combined with AND."
    print ""
    print "  [tags]                A comma-delimited list of tags. Photos with one or more"
    print "                        of the tags listed will be returned. You can exclude " 
    print "                        results that match a term by prepending it"
    print "                        with a - character."
    print "  [num]                 Max. num of images to download"
    print "  [access_token_file]   Access token file. Default: flickr_keyss.py"
    print ""
