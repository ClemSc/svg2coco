# svg2coco
Convert an SVG file into annotations in COCO format (JSON). Use your favorite vectoral drawing tool to create your computer vision training set.
I am a biologist, not a developper. Ideas and contributors are welcome !

## Features
Currently, only look for SVG paths and convert them in COCO path and bounding boxes (being the smallest retangle that encompass the path).
In case of multiclass, the current work-around in to use a different color for each classes (color name = class name; for now you have to make a find and replace, with sed or equivalent, in order to rename your classes.
