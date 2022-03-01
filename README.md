# svg2coco
Convert an SVG file into annotations in COCO format (JSON). Use your favorite vectoral drawing tool (actually, only Inkscape and Concept currently. Haha.) to create your computer vision training set.

Currently experimental. Please don't use it for production. Safer would be to regularly your COCO annotations with another software.

## Python dependencies
Requires Python 3.
Uses only standard libraries: argparse, glob, json, os, xml. 

## Features
- Currently, only look for SVG paths and convert them in COCO path and bbox (being the smallest retangle that encompass the path).

- SVG paths needs to be in the exact expected formats (empirically observed from paths produced with Inkscape free-hand tool and straight line path; with Concept free-hand tool.

- In case of multiclass, the current hack is to use a different stroke color for each classes (color name = class name; for now you have to make a find and replace, with sed or equivalent, in order to rename your classes.

## Missing features

- Assume that if you are using another software or another tool within those softwares, it is not going to work (universal parser of svg path should not be difficult to add, but not my next priority =)). I am a biologist, not a developper. Ideas and contributors are welcome !

- SVG layers and groups are not considered yet. It should work nonetheless, but script is not yet aware of transformations applied to a layer (translation for example). I recommend to be sure to not use layers and groups for now.

- More informations could be coded using svg path attribute: such as fill color for example.

- In practice, I am now working with the Concept drawing app on Android (using a stylus directly on touch display is the main idea for me). Concept is not free/open-source (a one time purchase is necessary to get the SVG export option). At this time, I am not aware of another good vectorial drawing tool with SVG. Recommandations are welcome.

## Usage

- Make sure that your SVG drawing board is fitting the image size. Also make sure that you export the whole board when saving the svg (and not crop to the actual drawing themself). In Concept, this is done using "Custom export".

- Should be also fine to leave the raster image embedded into the SVG file (I don't do it because I am working on quite large pictures).

- Don't trust blindly my code for now: check your first COCO annotations with another software and make sure that it works as you expect.

