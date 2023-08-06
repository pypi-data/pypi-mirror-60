"""
Module to take the resulting 3D reconstructions and print it as a 3D file such as wavefront .obj or .stl
"""
import numpy as np
import os.path as osp
# import matplotlib.pyplot as plt
from skimage import io, morphology, transform
import trimesh

def _extract_mask(s):
    """Helper function to always get a mask, if the array is not masked an array or zeros is returned"""
    if np.ma.isMaskedArray(s):
        array = s.data
        mask = s.mask
    else:
        array = s
        mask = np.zeros(s.shape)
    return [array, mask]


def _mask_it(reconstruction, mask=None):
    """Helper function to get a masked array of zeros if the input array is not masked"""
    if mask is None:
        return reconstruction
    if not mask.shape == reconstruction.shape:
        mask = reconstruction == 0
    return np.ma.array(reconstruction, mask=mask, fill_value=0)

def _with_texture(filename, valid, vertices, faces, texture):
    base, _ = osp.splitext(filename)
    shape = valid.shape
    Y, X = np.mgrid[:shape[0], :shape[1]]
    Y = 1 - Y / shape[0]
    X = X / shape[1]
    texture_array = np.vstack((X[valid], Y[valid])).T

    vertice_str = ('v {} {} {}\n' * len(vertices))[:-1].format(*vertices.flatten())
    texture_str = ('vt {} {}\n' * len(texture_array))[:-1].format(*texture_array.flatten())
    faces_str = ('f {}/{} {}/{} {}/{}\n' * len(faces))[:-1].format(*np.repeat(faces.flatten() + 1, 2))

    mtl_file = '{}.mtl'.format(base)
    with open(filename, 'w') as f:
        f.write('mtllib {}\n'.format(osp.basename(mtl_file)))
        f.write('\n')
        f.write(vertice_str)
        f.write('\n')
        f.write(texture_str)
        f.write('\n\nusemtl Textured\n')
        f.write(faces_str)

    texture_file = "{}_texture.png".format(base);
    io.imsave(texture_file, texture.astype(np.uint8));
    with open(mtl_file, 'w') as f:
        f.write("newmtl Textured\n")
        f.write("Ka 1.000 1.000 1.000\n")
        f.write("Kd 1.000 1.000 1.000\n")
        f.write("Ks 0.100 0.100 0.100\n")
        f.write("d 1.0\n")
        f.write("illum 2\n")
        f.write("map_Ka {}\n".format(osp.basename(texture_file)))
        f.write("map_Kd {}\n".format(osp.basename(texture_file)))


def _valid_triangles(vertex_inds, valid, neighbourhood, is_empty=None):
    shape = valid.shape
    new_valid = morphology.erosion(valid, neighbourhood)
    new_valid[-1, :] = 0; new_valid[:, -1] = 0
    if not is_empty is None:
        new_valid = new_valid & is_empty
    valid_inds = np.where(new_valid.flatten() == 1)[0]

    n = np.array(neighbourhood)[1:, 1:].astype(bool)
    first_vertex = 0 if n[0, 0] else 1
    second_vertex = shape[1] if n[1, 0] else shape[1] + 1
    third_vertex = shape[1] + 1 if n[1, 1] and second_vertex != shape[1] + 1 else 1

    triangles = np.vstack((vertex_inds[valid_inds + first_vertex],
                           vertex_inds[valid_inds + second_vertex],
                           vertex_inds[valid_inds + third_vertex])).T
    return triangles, new_valid

def _mesh_it(threeD, X, Y, valid):
    vertices = np.vstack((X[valid], Y[valid], threeD[valid])).T
    vertex_inds = np.cumsum(valid) - 1

    upper_right_triangles, upper_right_valid = _valid_triangles(vertex_inds, valid.astype(int), [[0, 0, 0], [0, 1, 1], [0, 0, 1]])
    lower_left_triangles, lower_left_valid = _valid_triangles(vertex_inds, valid.astype(int), [[0, 0, 0], [0, 1, 0], [0, 1, 1]])
    is_empty = ((upper_right_valid == 0) & (lower_left_valid == 0))
    upper_left_triangles, _ = _valid_triangles(vertex_inds, valid.astype(int), [[0, 0, 0], [0, 1, 1], [0, 1, 0]], is_empty)
    lower_right_triangles, _ = _valid_triangles(vertex_inds, valid.astype(int), [[0, 0, 0], [0, 0, 1], [0, 1, 1]], is_empty)

    faces = np.vstack((upper_right_triangles,
                       lower_left_triangles,
                       upper_left_triangles,
                       lower_right_triangles))
    return vertices, faces


_out_size = 2
def print_it(filename, threeD, texture=None, X=None, Y=None, xscale=1, yscale=1, absolute=False, downsampled_size=2**14):
    """
    Function to print a 3D array as a 3D file mesh. If it has more vertices than downsampled size it will be downscaled to appropriate size.
    Check trimesh library for which formats are supported

    Textures are only supported for wavefront .obj files

    X and Y will override the xscale and yscale parameters
    """
    _, mask = _extract_mask(threeD)
    transform_factor = int(np.ceil(np.sqrt(np.sum(~mask) / downsampled_size)))
    if transform_factor >= 1:
        threeD = transform.downscale_local_mean(threeD, (transform_factor, transform_factor))
        mask = transform.downscale_local_mean(mask.astype(float), (transform_factor, transform_factor))
    mask = mask > 0
    shape = threeD.shape
    valid = (~mask).astype(bool)



    if X is None or Y is None:
        general_scale = 2 * _out_size / (np.max(shape) - 1)
        Y, X = np.mgrid[:shape[0], :shape[1]]
        X =  (X - shape[1] / 2) * xscale * general_scale
        Y = -(Y - shape[0] / 2) * yscale * general_scale
        threeD *= general_scale / transform_factor
    else:
        X = transform.downscale_local_mean(X, (transform_factor, transform_factor))
        Y = transform.downscale_local_mean(Y, (transform_factor, transform_factor))

    vertices, faces = _mesh_it(threeD, X, Y, valid)
                
    ext = osp.splitext(filename)[1]
    if not texture is None and ext == '.obj':  # Textures only supported for this filetype currently
        _with_texture(filename, valid, vertices, faces, texture)
    else:
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh.export(filename)


def print_from_csv_file(reconstructed_file, ext):
    reconstructed_file_base, _ = osp.splitext(reconstructed_file)
    output_dir, file_name = osp.split(reconstructed_file)
    prefix = 'reconstructed_'
    base, ext = osp.splitext(file_name)

    reconstruction = np.loadtxt(reconstructed_file, dtype=float)

    segmented_file = osp.join(output_dir, 'segmented_{}.png'.format(base[len(prefix):]))
    global_segmentation_file_png = osp.join(output_dir, 'segmentation.png')
    global_segmentation_file_tif = osp.join(output_dir, 'segmentation.tif')
    mask = None
    if osp.isfile(segmented_file):
        segmented = io.imread(segmented_file, as_gray=True)
        mask = segmented == 0
    elif osp.isfile(global_segmentation_file_png):
        segmented = io.imread(global_segmentation_file_png, as_gray=True)
        mask = segmented == 0
    elif osp.isfile(global_segmentation_file_tif):
        segmented = io.imread(global_segmentation_file_tif, as_gray=True)
        mask = segmented == 0
    reconstruction = _mask_it(reconstruction, mask)

    texture_file = osp.join(reconstructed_file_base + '_texture.png')
    texture = None
    if osp.isfile(texture_file):
        texture = io.imread(texture_file)

    print_it('{}.{}'.format(reconstructed_file_base, ext), reconstruction, texture)
