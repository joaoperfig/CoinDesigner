#!/usr/bin/python

import numpy as np
import scipy.ndimage
import scipy.misc
from scipy import ndimage
import argparse
import normal_map_generator as nmg

mapfile = "normal_map_temp.png"

front_image = "coinparts/front.png"
left_image = "coinparts/left.png"
up_image = "coinparts/up.png"
right_image = "coinparts/right.png"
down_image = "coinparts/down.png"

res_x = 1040
res_y = 1040


def main():

    parser = argparse.ArgumentParser(description='Compute normal map of an image')

    parser.add_argument('input_file', type=str, help='input image path')
    parser.add_argument('output_file', type=str, help='output image path')
    parser.add_argument('-s', '--smooth', default=0., type=float, help='smooth gaussian blur applied on the image')
    parser.add_argument('-it', '--intensity', default=1., type=float, help='intensity of the normal map')
    parser.add_argument('-nmd', '--normalmaxdivide', default=1., type=float, help='divide max of normal map and clip it')
     
    args = parser.parse_args()

    sigma = args.smooth
    intensity = args.intensity
    input_file = args.input_file
    output_file = args.output_file
    nmd = args.normalmaxdivide


    im = ndimage.imread(input_file)
    #im = scipy.misc.imresize(im, (res_x, res_y), interp='bilinear', mode=None)
    
    if im.ndim == 3:
        im_grey = np.zeros((im.shape[0],im.shape[1])).astype(float)
        im_grey = (im[...,0] * 0.3 + im[...,1] * 0.6 + im[...,2] * 0.1)
        im = im_grey

    im_smooth = nmg.smooth_gaussian(im, sigma)

    sobel_x, sobel_y = nmg.sobel(im_smooth)

    normal_map = nmg.compute_normal_map(sobel_x, sobel_y, intensity, nmd)
    
    normal_map = scipy.misc.imresize(normal_map, (res_x, res_y), interp='bilinear', mode=None)
    
    
    #normal_map = ndimage.imread("wiki.png") #AAAAAA
    #normal_map = scipy.misc.imresize(normal_map, (res_x, res_y), interp='bilinear', mode=None)    #AAAAAA
    #normal_map = normal_map/255
    
    normal_map = normal_map/255
    print("NORMAL MAP")
    print(normal_map[3,3,0])
    print(normal_map[3,3,1])
    print(normal_map[3,3,2])
    
    scipy.misc.imsave(mapfile, normal_map)
    
    topness = np.zeros((res_x, res_y), dtype=np.float32)
    topness = normal_map[..., 1]
    topness = (topness - 0.5)*2
    topness = topness.clip(min=0, max=1)
    topness = topness**2    
    
    leftness = np.zeros((res_x, res_y), dtype=np.float32)
    leftness = 1-normal_map[..., 0]
    leftness = (leftness - 0.5)*2
    leftness = leftness.clip(min=0, max=1)    
    leftness = leftness**2
    
    downess = np.zeros((res_x, res_y), dtype=np.float32)
    downess = 1-normal_map[..., 1]
    downess = (downess - 0.5)*2
    downess = downess.clip(min=0, max=1)
    downess = downess**2
    
    rightness = np.zeros((res_x, res_y), dtype=np.float32)
    rightness = normal_map[..., 0]
    rightness = (rightness - 0.5)*2
    rightness = rightness.clip(min=0, max=1)    
    rightness = rightness**2
    
    inclination = np.zeros((res_x, res_y), dtype=np.float32)
    inclination = 1-(leftness+rightness+topness+downess)
    inclination = inclination.clip(min=0, max=1)
    
    scipy.misc.imsave("incl_temp.png", inclination)
    scipy.misc.imsave("incl_top.png", topness)
    scipy.misc.imsave("incl_left.png", leftness)
    scipy.misc.imsave("incl_right.png", rightness)
    scipy.misc.imsave("incl_down.png", downess)
    
    fi = (ndimage.imread(front_image)/255)**2
    li = (ndimage.imread(left_image)/255)**2
    ui = (ndimage.imread(up_image)/255)**2
    ri = (ndimage.imread(right_image)/255)**2
    di = (ndimage.imread(down_image)/255)**2
    
    result = np.zeros((res_x, res_y, 3), dtype=np.float32)
    result[..., 0] = (fi[..., 0]*inclination) + (li[..., 0]*leftness) + (ri[..., 0]*rightness) + (ui[..., 0]*topness) + (di[..., 0]*downess)
    result[..., 1] = (fi[..., 1]*inclination) + (li[..., 1]*leftness) + (ri[..., 1]*rightness) + (ui[..., 1]*topness) + (di[..., 1]*downess)
    result[..., 2] = (fi[..., 2]*inclination) + (li[..., 2]*leftness) + (ri[..., 2]*rightness) + (ui[..., 2]*topness) + (di[..., 2]*downess)
    
    result = (result*255)**0.5
    
    scipy.misc.imsave(output_file, result)


if __name__ == "__main__":
    main()
