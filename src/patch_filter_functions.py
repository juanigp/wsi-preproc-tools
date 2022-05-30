from registry import register_patch_filter_function

#calculate the areas of each patch for a tensor that was unfolded with the function get_patches
def calculate_areas(tensor):
    dims = tensor.dim()
    return tensor.sum(dim = dims-2).sum(dim = dims-2)

#get the indices of the foreground patches in an unfolded tensor
#based on area calculation, with content threshold 0.2
@register_patch_filter_function
def foreground_patches_filter_1(unfolded_tensor):
    mask_patches_areas = calculate_areas(unfolded_tensor)
    tile_size = unfolded_tensor.shape[-1]
    area_th = 0.2* tile_size * tile_size #0.05
    foreground_patches_idcs = mask_patches_areas > area_th
    return foreground_patches_idcs