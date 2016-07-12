# datr
Download data sets from flickr for given tags.

## Installation
1. ```git clone https://github.com/peerdavid/datr/```
2. Register on flickr and create an application: https://www.flickr.com/services/apps/create/apply/
3. Copy the new API_Key and API_SECRET.
4. Create a flickr_keys.py file (into the cloned dir) with the following content:<br>
``` python
API_KEY =  'YOUR_KEY'
API_SECRET = 'YOUR_SECRET'
```

## Execute
The following command will download 20 images with the tags car && red.
```# python datr.py car,red 20 ```


## Thanks to
https://github.com/alexis-mignon/python-flickr-api
