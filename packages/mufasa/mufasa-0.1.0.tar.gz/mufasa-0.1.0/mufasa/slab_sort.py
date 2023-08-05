__author__ = 'mcychen'

#=======================================================================================================================

import numpy as np
from scipy.ndimage.filters import median_filter

#=======================================================================================================================

def sort_2comp(data, method="linewidth"):
    if method == "linewidth":
        # move the larger linewidth the rare component
        swapmask = data[5] < data[1]
    return mask_swap_2comp(data, swapmask)


def quick_2comp_sort(data, filtsize=2):
    # use median filtered vlsr & sigma maps as a velocity reference to sort the two components

    # arange the maps so the component with the least vlsr errors is the first component
    swapmask = data[8] > data[12]
    data = mask_swap_2comp(data, swapmask)

    # the use the vlsr error in the first component as the reference and sort the component based on their similarities
    # to this reference (similary bright structures should have similar errors)
    ref = median_filter(data[8], size=(filtsize, filtsize))
    swapmask = np.abs(data[8] - ref) > np.abs(data[12] - ref)
    data = mask_swap_2comp(data, swapmask)

    def dist_metric(p1, p2):
        # use the first map (the one that should have the smallest error, hense more reliable) to compute
        #  distance metric based on their similarities to the median filtered quantity
        p_refa = median_filter(p1, size=(filtsize, filtsize))
        p_refb = median_filter(p2, size=(filtsize, filtsize))

        # distance of the current arangment to the median
        del_pa = np.abs(p1 - p_refa) #+ np.abs(p2 - p_refb)
        #del_pa = np.hypot(np.abs(p1 - p_refa), np.abs(p2 - p_refb))

        # distance of the swapped arangment to the median
        del_pb = np.abs(p2 - p_refa) #+ np.abs(p1 - p_refb)
        #del_pb = np.hypot(np.abs(p2 - p_refa),np.abs(p1 - p_refb))
        return del_pa, del_pb

    dist_va, dist_vb = dist_metric(data[0], data[4])
    dist_siga, dist_sigb = dist_metric(data[1], data[5])

    #swapmask = dist_va > dist_vb
    # use both the vlsr and the sigma as a distance metric
    swapmask = np.hypot(dist_va, dist_siga) > np.hypot(dist_vb, dist_sigb)

    data= mask_swap_2comp(data, swapmask)

    return data


def mask_swap_2comp(data, swapmask):
    # swap data over the mask
    data= data.copy()
    data[0:4,swapmask], data[4:8,swapmask] = data[4:8,swapmask], data[0:4,swapmask]
    data[8:12,swapmask], data[12:16,swapmask] = data[12:16,swapmask], data[8:12,swapmask]
    return data