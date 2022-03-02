#!/usr/bin/env python3

import argparse
from glob import glob
import json
from os.path import splitext, basename
from xml.dom import minidom

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input_dir", 
                        help="""Input directory for inference.""")
    
    return parser.parse_args()

def string2coord(string):
    """take a string such as "x,y" and return a list of two floats [x,y]"""
    return [float(x) for x in string.split(',')]

def d_bezier_to_straight_path(path_d):
    """
    Input:  d attribute of a svg path element coding for Bezier curve, relative mode.
            Typically produced by the free hand drawing tool of Inkscape.
    Output: is the list of points of this path (first point is absolute, 
            others relative to previous ones), without curve parameters.
    """
    path_d = path_d.split(' ')
    points = list()
    points.append(string2coord(path_d[1]))
    
    for i in range(5, len(path_d), 3):
        points.append(string2coord(path_d[i]))      
    return points

def d_straigh_to_straight_path(path_d):
    """
    Input:  is the d attribute of an svg path element representing a 
            straight path, relative mode. Typically produced by the straight line 
            tool of Inkscape.
    Output: is the list of points of this path (first point is absolute, 
            others relative to previous ones)
    """
    path_d = path_d.lstrip('m ').rstrip('z ').split(' ')
    points = list()
    for pt in path_d:
        points.append(string2coord(pt))
    return points

def d_qbezier_to_straight_path(path_d):
    """
    Input:  is the d attribute of an svg path element representing an absolute 
            quadratic Bezier path. Typically produced by the pen tool of 
            Concept (tested on Android).
    Output: is the list of absolute points of this path.
    """
    path_d2 = list()
    for i in path_d.split(' '):
        try:
            path_d2.append(float(i))
        except:
            pass
    
    points = list()
    for i in range(0, len(path_d2), 4):
        points.append([path_d2[i], path_d2[i+1]])    
    return points

def relative_path_to_absolute(points):   
    """
    Input:  list of relatives points (first point is absolute, others relative 
            to previous ones)
    Output: is the list of absolute points.
    """
    x = 0
    y = 0
    abs_path=list()
    for pt in points:
        x = pt[0] + x
        y = pt[1] + y
        abs_path.append([x,y])
    return abs_path

def translate_scale_round_path(viewBox, W_ratio, H_ratio, points):
    """
    Input:  list of absolute points. The path is translated and scaled 
            to be in original picture referential. Coordinates are rounded and made integers.
    Output: list of transformed points
    """
    ts_points = list()
    for pt in points:
        x = int(round((pt[0] - viewBox[0])*W_ratio))
        y = int(round((pt[1] - viewBox[1])*H_ratio))
        ts_points.append([x,y])
    return ts_points

def main():
    
    args = get_arguments()
    wd = args.input_dir.rstrip('/')
    
    # Get all svg in the folder.
    svg_file = glob(wd+'/*.svg')

    img_id = 0
    annot_id = 0
    annotations = list()
    images = list()
    
    # Looping into each images
    for svgf in svg_file:
        
        image_name = splitext(basename(svgf))[0] + '.jpg'
        psvgf = minidom.parse(svgf)
        
        # Collect informations on the svg drawing frame.
        # Svg viewBox
        viewBox = psvgf.getElementsByTagName('svg')[0].getAttribute('viewBox')
        viewBox = [float(n) for n in viewBox.split(' ')]
        viewBox_W, viewBox_H = viewBox[2], viewBox[3]
        
        # Image original width and height
        width = psvgf.getElementsByTagName('svg')[0].getAttribute('width')
        width = int(float(width.replace('px', '')))
        height = psvgf.getElementsByTagName('svg')[0].getAttribute('height').replace('px', '')
        height = int(float(height.replace('px', '')))

        # Scale ratio of the viewBox/original image
        W_ratio = width / viewBox_W
        H_ratio = height / viewBox_H
        
        # Add image informations in COCO fields
        images.append({
                    'id': img_id,
                    'file_name': image_name,
                    'height': height,
                    'width': width
                      })
        
        # Collect all paths
        allpath = [path for path in psvgf.getElementsByTagName('path')]

        for path in allpath:
            
            d = path.getAttribute('d')
            categorie = path.getAttribute('stroke')

            # Identifying the format of the path (really limited options now, and assume that path
            # are not mixing commands. Should be replaced by a more universal 
            # svg-path parsing function).
            
            if 'c' in d:
                #print('Found c command, assuming 'Inkscape-style' relative Bezier curves')
                points = d_bezier_to_straight_path(d)
                points = relative_path_to_absolute(points)
                points = translate_scale_round_path(viewBox, W_ratio, H_ratio, points)
                
            elif 'Q' in d:
                #print('Found Q command, assuming 'Concept-style' Q Bezier curves')
                points = d_qbezier_to_straight_path(d)
                points = translate_scale_round_path(viewBox, W_ratio, H_ratio, points)
        
            elif 'm' in d:
                #print('assuming 'Inkscape-style' straight relative path')
                points = d_straigh_to_straight_path(d)
                points = relative_path_to_absolute(points)
                points = translate_scale_round_path(viewBox, W_ratio, H_ratio, points)
                
            # Getting minimal, unrotated,  bounding box coordinates
            minx = min([i[0] for i in points])
            maxx = max([i[0] for i in points])
            miny = min([i[1] for i in points])
            maxy = max([i[1] for i in points])
            
            # Flattening coordinates list, as in COCO segmentation field.
            points = [pt for sublist in points for pt in sublist]
            annotations.append({'id':annot_id,
                                'categorie_name': categorie,
                                'segmentation': [points],
                                'image_id': img_id,
                                'iscrowd': 0,
                                'bbox:':[minx, miny, maxx-minx, maxy-miny],
                                'area': (maxx-minx) * (maxy-miny)})
            annot_id+=1
        img_id+=1

    # Indexing categories:
    categories = list()
    cat = list(set([a['categorie_name'] for a in annotations]))
    cat.sort()
    mapper = dict(zip(cat,range(0,len(cat),1)))

    # Making the COCO categories field. Supercategory remains blank (unused currently).
    for k,v in mapper.items():
        categories.append({'id': v,
                        'name':k,
                        'supercategory':''})
        
    # Adding category id to annotations.
    for a in annotations:
        a['categorie_id'] = mapper[a['categorie_name']]
        del a['categorie_name']
        
    coco = {'images':images,
        'annotations':annotations,
        'categories':categories,
        'type':'',
        'licenses': '',
        'info': ''}
    
    print(json.dumps(coco, indent=4))
    
    return coco

if __name__ == "__main__":
    main()