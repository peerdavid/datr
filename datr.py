#
# datr
# Download data sets from flickr
# See also https://github.com/peerdavid/datr
#
import sys
import os
import flickr_api as f
from flickr_api import Walker
import urllib


try :
    search_tags = sys.argv[1]
    num_img = int(sys.argv[2])
    
    license = ""
    if len(sys.argv) == 4:
        license = sys.argv[3]

    os.popen('rm -r download/')
    os.popen('mkdir download')
    
    print "Downloading images with tags '" + search_tags + "'"
    if license != "":
        print "License type set to " + license + "\n" 
    else:
        print "License type set to any \n"

    w = Walker(f.Photo.search, tags=search_tags, tag_mode='all', extras='url_s', license=license, sort='interestingness-desc')
    i = 0
    for photo in w:
        i += 1
        if i >= num_img:
            break
        print "Downloading image | Title = '" + photo.title + "' | License = " + photo.license
        urllib.urlretrieve(photo.url_s, "download/image-" + str(i) + ".jpg")
   
    print "\nDone."
    print "Downloaded " + str(i) + " images. \n"
         
         
except IndexError :
    print ""
    print "Usage: python datr.py [tags] [num_images] [license]"
    print "Download a data set from flickr for given tags. All tags will be combined with AND."
    print ""
    print "  [tags]                A comma-delimited list of tags. Photos with one or more"
    print "                        of the tags listed will be returned. You can exclude " 
    print "                        results that match a term by prepending it"
    print "                        with a - character."
    print "  [num_images]          Max. num of images to download"
    print "  (optional)[license]   Select the license of the images:"
    print "                           0 - All Rights Reserved"
    print "                           4 - Attribution License"
    print "                           6 - Attribution-NoDerivs License"
    print "                           3 - Attribution-NonCommercial-NoDerivs License"
    print "                           2 - Attribution-NonCommercial License"
    print "                           1 - Attribution-NonCommercial-ShareAlike License"
    print "                           5 - Attribution-ShareAlike License"
    print "                           7 - No known copyright restrictions"
    print "                           8 - United States Government Work"
    print "                           9 - Public Domain Dedication (CC0)"
    print "                          10 - Public Domain Mark "
    print ""
