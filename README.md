# svg2coco
Convert an SVG file into annotations in COCO format (JSON). Use your favorite vectoral drawing tool (actually, only Inkscape and Concept currently, hehehe...) to create your computer vision training set.

Currently experimental. Please don't use it for production. Safer would be to regularly check your COCO annotations with another software. I am a biologist, not a developper. Ideas and contributors are welcome !

## Python dependencies
Requires Python 3.
Uses only standard libraries: argparse, glob, json, os, xml. 

## Usage

    svg2coco.py -i ./input_dir > coco_annotation.json


Just specify the input directory with -i/--input_dir and redirect the output (COCO JSON string) to a new file.

The input directory needs to contain the set of svg containing your annotations. Each \<path> from all svg will be 
selected and converted to an annotation. Images name is infered from the svg file names: mypict.svg --> pypict.jpg. Mind that if your images have a different extension than "jpg", you will want to adjust this.

The hexadecimal code of the stroke color of the path will be used as category_name. Its up to the user to manage this somehow :).
The 'iscrowd' field default to zero (I don't need it). If you are interested in it, it could be easily encoded using another svg path property such as stroke style, fill color or something else. Then it is 2 lines of code to add.


## When drawing

- Make sure that your SVG drawing board (= page size, = width and height of svg document) is fitting the original image size. Import the image, resize page to drawing, then start drawing. Also make sure that you export the whole board/page when saving the svg (do not let your software crop to the actual drawing). In Concept, this is done using "Custom export".

- Should be also fine to leave the raster image embedded into the SVG file (I don't do it because I am working on quite large pictures).


## Features and limitations
- Currently, look only for SVG paths and convert them in COCO path and bbox (being the smallest retangle that encompass the path). Other SVG element such as rect or circle are disregarded.

- SVG paths needs to be in the exact expected formats (empirically observed from paths produced with Inkscape free-hand tool and straight line tool, and with Concept free-hand tool.

- In case of multiclass, the current hack is to use a different stroke color for each classes (color name = class name; for now you have to make a find and replace, with sed or equivalent, in order to rename your classes.

- Assume that if you are using another software or another tool within those softwares, it is not going to work (universal parser of svg path should not be difficult to add, but not my next priority =)).

- SVG layers and groups are not considered yet. It should work nonetheless, but script is not yet aware of transformations applied to a layer (translation for example).

- More informations could be coded using further svg path attributes: fill color, stroke style...

- In practice, I am now working with the Concept drawing app on Android (using a stylus directly on touch display is the main idea for me). Concept is not free/open-source (a one time purchase is necessary to get the SVG export option). At this time, I am not aware of another good vectorial drawing tool with SVG. Recommendations are welcome.

- Don't trust blindly my code for now: check your first COCO annotations and make sure that it works as you expect.
