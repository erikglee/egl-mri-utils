import nibabel as nib

def make_dscalar_cifti(data_array, template_cifti_path, output_cifti_path, dimension_names=None):
    """
    #Function that creates a cifti dscalar.nii file for
    #visualizing overlays. data_array should  have a shape
    #<n_dimensions, n_regions> where n_dimensions is at least
    #1. template_cifti_path is the path to a cifti file (either
    #pscalar or ptseries works) that has the same parcel definitions
    #as desired for visualizing the data_array. Output_cifti_path
    #specifies the name of the file to be saved (should end in
    #*.pscalar.nii). dimension_names is optional list that will serve
    #as the name of different dimensions (i.e. PC1, PC2, etc.). If
    #specified, dimension_names should have one element for each dimension
    #(not region) in data_array. Function saves new file to output path,
    #doesn't return anything
    """
    
    #Set dimension names if not specified
    if type(dimension_names) == type(None):
        dimension_names = ['NONAME']*data_array.shape[0]
    
    #Load template cifti file
    template_cifti = nib.load(template_cifti_path)
    
    #Copy/generate axis for new cifti file
    dscalar_axis_1 = template_cifti.header.get_axis(1)
    dscalar_axis_0 = nib.cifti2.cifti2_axes.ScalarAxis(dimension_names)
    
    #Put the axes into a header
    cifti_hdr = nib.cifti2.cifti2_axes.to_header([dscalar_axis_0, dscalar_axis_1])
    
    #put the data array and axes into a new image
    cifti_image = nib.cifti2.cifti2.Cifti2Image(dataobj=data_array, header=cifti_hdr)
    
    #Save the cifti image
    nib.save(cifti_image, output_cifti_path)
    
    return