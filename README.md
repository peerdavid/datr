# datr
Download image sets from flickr -> create your own training set for machine learning tasks etc.

## Usage
1. ```git clone https://github.com/peerdavid/datr/```
2. Register on flickr and create an application: https://www.flickr.com/services/apps/create/apply/
3. Copy the new API_Key and API_SECRET.
4. Create a flickr_keys.py file (into the cloned dir) with the following content:<br>
``` python
API_KEY =  'YOUR_KEY'
API_SECRET = 'YOUR_SECRET'
```

## Execute
```
Usage: datr.py [options]

Options:
  -h, --help            show this help message and exit
  -s SEARCH_TAGS, --search_tags=SEARCH_TAGS
                        A comma-delimited list of tags. Photos with one or
                        moreof the tags listed will be returned. You can
                        exclude results that match a term by prepending itwith
                        a - character.
  -f, --use-free-text   Use free text search, if not enough images are
                        available
  -t NUM_THREADS, --num_threads=NUM_THREADS
                        Number of downloader threads (speed up download)
  -p PATH, --path=PATH  Path where downloaded files should be saved
  -n MAX_NUM_IMG, --num_images=MAX_NUM_IMG
                        Max. number of images to download
  -l LICENSE, --license=LICENSE
                        License of images. 0=All Rights Reserved,
                        4=Attribution License, 6=Attribution-NoDerivs License,
                        3=Attribution-NonCommercial-NoDerivs License, 2
                        =Attribution-NonCommercial License, 1=Attribution-
                        NonCommercial-ShareAlike License, 5=Attribution-
                        ShareAlike License, 7=No known copyright restrictions,
                        8=United States Government Work, 9=Public Domain
                        Dedication (CC0) 10=Public Domain Mark
```

### Example
The following command will download 50 (Public Domain Dedication (CC0) license) images tagged with 'car'. 
To speed up the download we start 20 downloader threads.<br>

```
user@ubuntu:~/Dev/datr$ python datr.py --num_images 50 --search_tags car --license 9 --num_threads 20
Starting 20 downloader threads
Downloading images for search tags car and license 9.

Downloaded image download/28048280xxx.jpg | Title = '...' | License = 9
Downloaded image download/28152122xxx.jpg | Title = '...' | License = 9
Downloaded image download/27870814xxx.jpg | Title = '...' | License = 9
[...]
Downloaded image download/28048283xxx.jpg | Title = '...' | License = 9

Finished image download after 6.88 sec.

```

## Thanks to
https://github.com/alexis-mignon/python-flickr-api
