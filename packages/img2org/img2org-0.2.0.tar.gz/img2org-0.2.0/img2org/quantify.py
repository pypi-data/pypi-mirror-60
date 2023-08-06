#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:34:13 2020

@author: henrik
"""

import numpy as np
from skimage.morphology import binary_dilation
from skimage.measure import marching_cubes_lewiner
from skimage.measure import mesh_surface_area
from skimage.segmentation import relabel_sequential
from phenotastic.misc import autocrop, cut
import mahotas as mh

def get_wall(seg_img, cell1, cell2, selem=None, intensity_image=None, crop=True):
    """
    Finds voxels of cell walls between 2 specified cells.
    Output is a 3D numpy array for each cell i containing:
        True on voxels of cell i neighbouring the other cell
        False otherwise
    
    segmentedImage --- 3D numpy array of cell labels in image
    cell1 --- integer label of cell1
    cell2 --- integer label of cell2
#    thickness --- wall thickness (default 1 voxel)
    """
#    cell1Img = np.zeros_like(segmentedImage, dtype=bool)
#    cell1Img[np.where(segmentedImage == cell1)] = True
#    cell2Img = np.zeros_like(segmentedImage, dtype=bool)
#    cell2Img[np.where(segmentedImage == cell2)] = True
    
    # Dilate each cell by thickness and walls are the intersection
    
#    cell1ImgDil = binary_dilation(cell1Img, selem=selem)
#    cell2ImgDil = binary_dilation(cell2Img, selem=selem)
#    overlap = cell1ImgDil & cell2ImgDil
    border = mh.border(seg_img, cell1, cell2, Bc=selem)

    vals1, vals2 = None, None    
    if crop:
        border, cuts = autocrop(border, n=1, threshold=0, return_cuts=True, offset=[[2,2], [2,2], [2,2]])
        seg_section = cut(seg_img, cuts)
    wall1 = np.logical_and(border, seg_section == cell1)
    wall2 = np.logical_and(border, seg_section == cell2)

    if intensity_image is not None:
        if crop:
            intensity_image = cut(intensity_image, cuts)
        vals1 = intensity_image[wall1]
        vals2 = intensity_image[wall2]
    
    return wall1, wall2, vals1, vals2

def get_l1(seg_img, bg=0, selem=None):
    bg_dilated = np.logical_and(binary_dilation(seg_img==bg, selem=selem), seg_img)
    
    labels = np.unique(seg_img)
    labels = labels[labels != bg]
    l1 = np.unique(seg_img[bg_dilated])
    l1 = l1[l1 != bg]
    l1 = np.isin(labels, l1)
    return l1


def area_between_walls(wall1, wall2, voxel_dims=(1,1,1)):
    """
    Finds surface area of contact between 2 specified cell walls.
    Output is a float value, with units [voxel_dim units]**2
    
    wall1 --- 3D numpy array containing True on voxels of wall1, as ouputted
              by the get_wall function
    wall2 --- 3D numpy array of the same size for wall2
    voxel_dims --- 3-tuple of voxel dimensions
    """
    voxel_dims = tuple(voxel_dims)  # in case list object was given
    
    # Create mesh of walls using marching cubes algorithm
    verts1, faces1, _, _ = marching_cubes_lewiner(wall1, spacing=voxel_dims)
    verts2, faces2, _, _ = marching_cubes_lewiner(wall2, spacing=voxel_dims)
    verts1, verts2 = list(map(tuple, verts1)), list(map(tuple, verts2))
    
    # Find vertices in mesh common between walls
    my_verts = []
    vert_inds = []
    for i, v in enumerate(verts1):
        if v in verts2:
            my_verts.append(v)
            vert_inds.append(i)
    my_verts = np.array(my_verts)
    
    # Keep triangles which connect these vertices
    my_faces = []
    for f in faces1:
        if set(f).issubset(vert_inds):
            my_faces.append(f)
    my_faces = np.array(my_faces, dtype=int)
    
    # If no faces in common, return 0 surface area
    if my_faces.size == 0:
        return 0
    
    # Relabel vertex indices in my_faces
    relab, fw, inv = relabel_sequential(np.array(vert_inds))
    for old, new in enumerate(fw):
        my_faces[my_faces == old] = new
    if vert_inds[0] != 0:    # relabel_sequential function doesn't remap to 0
        my_faces -= 1
    
    # Plot mesh with mayavi
#    mlab.triangular_mesh(my_verts[:,0], my_verts[:,1], my_verts[:,2], my_faces)
#    mlab.show()
    
    # Calculate surface area of new mesh
    return mesh_surface_area(my_verts, my_faces)

def quantify_signal(image, voxels):
    """
    Measures total signal (e.g. PIN) on specified 'True' voxels.
    
    image --- 3D numpy array of image signal (e.g. intensity of PIN:GFP)
    voxels --- 3D numpy array of same size, containing bools.
    """
    values = np.array(image[voxels == True])
    total_signal = np.sum(values)
    return total_signal

def set_background(seg_img, bg=0, mode='largest'):
    labels, counts = np.unique(seg_img, return_counts=True)
    swap_label = labels[np.argmax(counts)]
    
    old_background = seg_img == bg
    new_background = seg_img == swap_label
    seg_img[old_background] = swap_label
    seg_img[new_background] = bg
    
    return seg_img

def find_neighbors(seg_img, bg=None, selem=None):
    """
    Output dictionary with the n-th entry being a list of labels of regions
    which border the n-th region, and a list of the respective contact areas
    
    img_in --- 3D array of region labels
#    ignoreZero --- Boolean to say whether regions with label 0 are ignored
    voxel_dims --- 3-tuple of voxel dimensions, used to calculate areas
    """
    from phenotastic.misc import autocrop
    labels = np.unique(seg_img)
    if bg is not None:
        labels = labels[labels != bg]
    
    neighs = {}
    for region in labels:
        
        print("Finding neighbors of " + str(region))
        mask, cuts = autocrop(seg_img == region, n=1, threshold=0, offset=[[2,2], [2,2], [2,2]], return_cuts=True)
        seg_section = seg_img[cuts[0,0]:cuts[0,1],cuts[1,0]:cuts[1,1],cuts[2,0]:cuts[2,1]]
        mask = binary_dilation(mask, selem=selem)
        cell_neighbours = np.unique(seg_section[mask])
        cell_neighbours = cell_neighbours[cell_neighbours != region]
    
        if bg is not None:
            cell_neighbours = cell_neighbours[cell_neighbours != bg]
        
        neighs[region] = cell_neighbours
        
    return neighs