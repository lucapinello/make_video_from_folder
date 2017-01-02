'''
Create a video from a folder of jpg images,
sorting the images by capture time.

Luca Pinello 2017

'''

import glob
import numpy as np
from PIL import Image, ExifTags
import glob
import os
import time
import imageio
import datetime


imageio.plugins.ffmpeg.download()

VIDEO_SIZE=(1376,912)
FPS=3
VIDEO_FILENAME='IMG_MOVIE.AVI'

#get the right field code
for exif_orientation in ExifTags.TAGS.keys() : 
    if ExifTags.TAGS[exif_orientation]=='Orientation' : break 
        
for exif_datetime in ExifTags.TAGS.keys() : 
    if ExifTags.TAGS[exif_datetime]=='DateTime' : break


def resize_rotate_and_crop(img_path, size, crop_type='middle'):
    """
    Resize and crop an image to fit the specified size.
    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    
    try: 
        #rotate if necessary
        exif=dict(img._getexif().items())
        if exif[exif_orientation] == 3:
                img=img.rotate(180, expand=True)
        elif exif[exif_orientation] == 6:
            img=img.rotate(270, expand=True)
        elif exif[exif_orientation] == 8:
            img=img.rotate(90, expand=True)
    except:
        print img_path
    
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    return img

print '''
 _____                                 
|_   _|                                
  | | _ __ ___   __ _  __ _  ___  ___  
  | || '_ ` _ \ / _` |/ _` |/ _ \/ __| 
 _| || | | | | | (_| | (_| |  __/\__ \ 
 \___/_| |_| |_|\__,_|\__, |\___||___/ 
                       __/ |           
                      |___/            
 _                _     _              
| |              (_)   | |             
| |_ ___   __   ___  __| | ___  ___    
| __/ _ \  \ \ / / |/ _` |/ _ \/ _ \   
| || (_) |  \ V /| | (_| |  __/ (_) |  
 \__\___/    \_/ |_|\__,_|\___|\___/   
                                                                              

'''

print 'Create a video from a folder with images! Luca Pinello 2017\n\n\n'


print 'Sorting files by capture time in the exif metadata...'
#sort filenames by timestamp
flist=glob.glob("*.jpg")
dic = dict()
for fname in flist:
    
     img=Image.open(fname)
     exif=dict(img._getexif().items())
     timestamp = int(time.mktime(datetime.datetime.strptime(exif[exif_datetime], '%Y:%m:%d %H:%M:%S').timetuple()))
     
     try:
         dic[timestamp] = fname
     except:
         print fname, ' not processed.'

keys = dic.keys()
keys.sort()

filenames=[]
for k in keys:
    filenames.append(dic[k])
print 'Done'

print 'Creating video...'
#Write video
with imageio.get_writer(VIDEO_FILENAME, mode='I',fps=FPS) as writer:
    for idx,filename in enumerate(filenames):
        im=resize_rotate_and_crop(filename, VIDEO_SIZE)
        writer.append_data(np.asarray(im))
        if (idx % 100)==0:
            print 'Processed %d images of %d' % (idx+1, len(filenames))

print 'All done! Enjoy your video'
