# -*- coding: utf-8 -*-
# author:
# - XuWei, initialize 
# - LiaoPan, Integration
"""
Optical Scanning Data Preprocess
"""
import os
import copy
import mne
import numpy as np
import open3d as o3d


def trans_point_cloud_data(opt_point_cloud_filename, output_point_cloud_filename):
    """
    transform opitcal scanning point cloud data to ras(mri) coordinate.
    """
    trans_matrix_240122_to_ras = np.array(
        [[-1.219196101118701359e-01, -9.896540046547318559e-01, 7.563438200330221961e-02, -3.903328006119257054e+01],
         [9.920811405776109870e-01, -1.238257273540025460e-01, -2.102854620458653387e-02, 4.987221084469649668e+01],
         [3.017646732796550046e-02, 7.247165181023616787e-02, 9.969138581158855095e-01, -5.012311685697530947e+02],
         [0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00, 1.000000000000000000e+00]])

    trans = trans_matrix_240122_to_ras
    pcd = o3d.io.read_point_cloud(str(opt_point_cloud_filename))
    pcd.transform(trans)
    o3d.io.write_point_cloud(str(output_point_cloud_filename), pcd)


def get_trans_fif(opt_point_cloud_filename, mri_point_cloud_filename, subject_name, output_trans_dir, visual_check):
    """
    get trans.fif for registration.
    Parameters
    ----------
    opt_point_cloud_filename: str
     - optical scanning data
    mri_point_cloud_filename: str
     - mri surface point cloud data
    subject_name: str
     - subject name
    output_trans_dir: str
     - the trans matrix folder.
    visual_check: bool
     -  visual check the result of icp algorithm.
     
    """
    source = o3d.io.read_point_cloud(str(opt_point_cloud_filename))  # source 为需要配准的点云
    source.points = o3d.utility.Vector3dVector(np.asarray(source.points) / 1000)
    # target = read_point_from_txt(mri_point_cloud_filename,unit='m')  # target 为目标点云
    target = read_point_from_ply(str(mri_point_cloud_filename), unit='m')  # target 为目标点云

    # 为两个点云上上不同的颜色
    source.paint_uniform_color([1, 0.706, 0])  # source 为黄色
    target.paint_uniform_color([0, 0.651, 0.929])  # target 为蓝色

    trans_init = np.asarray([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0.0, 0.0, 0.0, 1.0]])
    # ICP Iter.
    reg_p2p = o3d.pipelines.registration.registration_icp(source, target, 500, trans_init,
                                                          o3d.pipelines.registration.TransformationEstimationPointToPoint(
                                                              with_scaling=False))
    r = mne.transforms.Transform(4, 5, reg_p2p.transformation)
    if not os.path.exists(output_trans_dir):
        os.makedirs(output_trans_dir)
    trans_fname = os.path.join(output_trans_dir, f'{subject_name}-trans.fif')
    r.save(trans_fname, overwrite=True)
    if visual_check:
        draw_registration_result(source, target, reg_p2p.transformation)
    return trans_fname


def read_point_from_ply(fname_ply, unit='m'):
    source = o3d.io.read_point_cloud(fname_ply)
    dat = np.asarray(source.points)
    if unit == 'm':
        xyz = dat / 1000
    elif unit == 'mm':
        xyz = dat
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    return pcd


def read_point_from_txt(fname_txt, unit='m'):
    """
    Deprecated code
    """
    dat = np.loadtxt(fname_txt)
    if unit == 'm':
        xyz = dat[:, 0:3] / 1000
    elif unit == 'mm':
        xyz = dat[:, 0:3]
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    if dat.shape[1] >= 6:
        nxyz = dat[:, 3:6]
        nxyz = nxyz / np.sqrt(np.sum(nxyz ** 2, 1))[:, np.newaxis]
        pcd.normals = o3d.utility.Vector3dVector(nxyz)
    return pcd


def draw_registration_result(source, target, transformation):
    """origin from open3d.
    """
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])
