# YAGCS - Yet Another GeoCache Submitter
YAGCS takes an image with co-oordinates in EXIF as input and:
* reads co-ordinates from image
* reverse geocode the co-ordinates for a geocache name
* login to geocaching.com
* creates a geocache listing
* upload spoiler picture
* submits the geocache for review

## Warning
Experimental software, use on your own risk!
Usage may violate geocaching terms and conditions.

## Requirements
Needs libraries: exifread, requests, selenium, time
