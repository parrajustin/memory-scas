
Install the following packages with venv

easyocr                  1.7.2
google-api-python-client 2.156.0
google-cloud-vision      3.9.0
opencv-python            4.10.0.84

Use prompt.py to get the images saved

use cloud.py to get the text

use the following to set exif data

```
exiftool -DateTimeOriginal="2006:01:01 01:01:01" -EXIF:DateTimeOriginal
="2006:01:01 01:01:01" -XMP:CreateDate="2006:01:01 01:01:01" -EXIF:CreateDate="2006:01:01 01:01:01" -XMP:DateTimeOriginal="2006:01:01 01:01:01
" -ImageDescription="Mom & Dad Wedding" -XMP-dc:Description="Mom & Dad Wedding" -overwrite_original ./scan_32_front.png
```

use the following to set all dates to 1980 for the png

```
exiftool -DateTimeOriginal="1980:01:01 01:01:01" -EXIF:DateTimeOriginal="1980:01:01 01:01:01" -XMP:CreateDate="1980:01:01 01:01:01" -EXIF:CreateDate="1980:01:01 01:01:01" -XMP:DateTimeOriginal="1980:01:01 01:01:01" -overwrite_original ./*.png
```
