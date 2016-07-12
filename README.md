# datr
Download data sets from flickr for given tags.

## Configuration
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
Usage: python datr.py [tags] [num_images] [license]
Download a data set from flickr for given tags. All tags will be combined with AND.
  [tags]                A comma-delimited list of tags. Photos with one or more
                        of the tags listed will be returned. You can exclude 
                        results that match a term by prepending it
                        with a - character.
  [num_images]          Max. num of images to download
  (optional)[license]   Select the license of the images:
                           0 - All Rights Reserved
                           4 - Attribution License
                           6 - Attribution-NoDerivs License
                           3 - Attribution-NonCommercial-NoDerivs License
                           2 - Attribution-NonCommercial License
                           1 - Attribution-NonCommercial-ShareAlike License
                           5 - Attribution-ShareAlike License
                           7 - No known copyright restrictions
                           8 - United States Government Work
                           9 - Public Domain Dedication (CC0)
                          10 - Public Domain Mark 
```

### Example
The following command will download 10 images of red cars with Public Domain Dedication (CC0) license.<br>
```
ubuntu:~/Dev/datr$ python datr.py car,red 10 9
Downloading images with tags 'car,red'
License type set to 9

Downloading image #1 | Title = '20150524_133712LC' | License = 9
Downloading image #2 | Title = 'Under the Hood' | License = 9
Downloading image #3 | Title = '1935 Auburn 851 S/C Boattail Speedster' | License = 9
Downloading image #4 | Title = '1931 Cadillac' | License = 9
Downloading image #5 | Title = 'Zoom' | License = 9
Downloading image #6 | Title = 'rusty car 2' | License = 9
Downloading image #7 | Title = 'rusty car 1' | License = 9
Downloading image #8 | Title = 'DSC00249' | License = 9
Downloading image #9 | Title = 'River bank ahead' | License = 9

Done.
Downloaded 10 images. 
```

## Thanks to
https://github.com/alexis-mignon/python-flickr-api
