import nibabel as nib
import numpy as np
import os, glob, tempfile
import pandas as pd

def dconn_from_dtseries_list_lowmem(input_paths, output_dconn_path, volumes_to_drop=None, chunk_size=1000):
    """
    Calculates a dense connectivity matrix (dconn) from a series of dtseries files
    using a low-memory chunked approach, removing specific volumes. Scrubbing is allowed
    with the volumes_to_drop command.
    
    Prior to concatenation all greyordinate timeseries within a run will be z-scored
    so that each timepoint contributes equally to the final correlation estimates.
    
    Parameters:
    - input_path: List of paths to input .dtseries.nii
    - output_dconn_path: Path to save output .dconn.nii
    - volumes_to_drop: List of Lists or arrays of 0-based indices to remove (e.g. [0, 1, 15, 20]).
    - chunk_size: Number of rows (greyordinates) to process at once.
    """
    
    if (len(input_paths) != len(volumes_to_drop)) and (volumes_to_drop is not None):
        raise ValueError('Error: found {} input_paths and {} volumes_to_drop'.format(len(input_paths), len(volumes_to_drop)))
    
    data_zscored_list = []
    for i, temp_input in enumerate(input_paths):
    
        print(f"Loading {temp_input}...")
        cifti_img = nib.load(temp_input)
        data_full = cifti_img.get_fdata()

        n_total_timepoints = data_full.shape[0]

        # 1. Slice volumes based on specific indices
        if volumes_to_drop is not None and len(volumes_to_drop[i]) > 0:
            print(f"Dropping {len(volumes_to_drop[i])} specific volumes...")

            # Create an array of all possible indices (0 to N-1)
            all_indices = np.arange(n_total_timepoints)

            # Find indices that are NOT in the drop list
            keep_indices = np.setdiff1d(all_indices, volumes_to_drop[i])

            if len(keep_indices) == 0:
                raise ValueError("Error: You are dropping all volumes in the file.")

            # Select only the indices we want to keep
            data_sliced = data_full[keep_indices, :]
        else:
            print("No volumes dropped. Using full time series.")
            data_sliced = data_full

        n_timepoints, n_greyordinates = data_sliced.shape
        print(f"Data dimensions after censoring: {n_timepoints} timepoints x {n_greyordinates} vertices")

        # 2. Normalize Data (Z-score / Unit Vector Scaling)
        print("Normalizing time series data...")

        # Subtract mean
        data_centered = data_sliced - data_sliced.mean(axis=0)
        
        # Calculate Standard Deviation
        data_std = data_centered.std(axis=0)
        data_std[data_std == 0] = 1e-9 # Prevent division by zero
        
        # Z-score
        data_zscored = data_centered / data_std
        data_zscored_list.append(data_zscored)
        
        # Free up memory
        del data_full
        del data_sliced
        del data_centered
        
    # 2.5. Concatenate and L2 Normalize Globally
    print("Concatenating and globally L2-normalizing time series...")
    data_concat = np.vstack(data_zscored_list)
    del data_zscored_list # free memory
    
    # Calculate global L2 norm across all concatenated timepoints
    norms = np.sqrt((data_concat ** 2).sum(axis=0))
    norms[norms == 0] = 1e-9 
    
    # Final data ready for matrix multiplication
    data_normalized_concat = data_concat / norms
    del data_concat # free memory
        
    # 3. Prepare Memory-Mapped Output
    print("Initializing memory-mapped file for output matrix...")
    temp_dir = tempfile.mkdtemp()
    temp_memmap_path = os.path.join(temp_dir, 'temp_dconn.dat')
    
    # Create memmap (Space x Space)
    dconn_memmap = np.memmap(temp_memmap_path, dtype='float32', mode='w+', 
                             shape=(n_greyordinates, n_greyordinates))

    # 4. Calculate Correlation in Chunks
    print(f"Computing correlation in chunks of {chunk_size} rows...")
    
    for i in range(0, n_greyordinates, chunk_size):
        end_idx = min(i + chunk_size, n_greyordinates)
        
        # Get chunk (Time x Chunk)
        chunk_data = data_normalized_concat[:, i:end_idx]
        
        # Matrix Multiply: (Chunk_T) dot (All_Data)
        chunk_corr = np.dot(chunk_data.T, data_normalized_concat)
        
        # Write to disk
        dconn_memmap[i:end_idx, :] = chunk_corr
        
        # Periodically flush to disk to save RAM
        if i % (chunk_size * 5) == 0:
            print(f"  Processed rows {i} to {end_idx}...")
            dconn_memmap.flush()

    print("Calculation complete. Preparing CIFTI header...")

    # 5. Create Header and Save
    brain_axis = cifti_img.header.get_axis(1)
    new_header = nib.cifti2.Cifti2Header.from_axes((brain_axis, brain_axis))
    
    out_img = nib.cifti2.Cifti2Image(dconn_memmap, header=new_header)
    out_img.nifti_header['descrip'] = b'Created with low-mem Python script (censored)'

    print(f"Saving final .dconn.nii to {output_dconn_path}...")
    out_img.to_filename(output_dconn_path)

    # 6. Cleanup
    try:
        del dconn_memmap
        os.remove(temp_memmap_path)
        os.rmdir(temp_dir)
        print("Temporary files cleaned up.")
    except Exception as e:
        print(f"Warning: Could not remove temp file. {e}")

    print("Done!")