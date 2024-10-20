# -*- coding: utf-8 -*-
# author:
# - LiaoPan for integration and pipeline
# - XuWei for the init version
# purposes:
#   Preprocessing pipeline for OPM-MEG

import os
import mne
import numpy as np
from opm.coregistration import gen_bem_from_anat, get_face_from_anat, run_freesurfer
from opm.coregistration import get_trans_fif, trans_point_cloud_data
from opm.source_imaging import lcmv


class OPM(object):
    """
    The Main Pipeline Object.
    For opticallly pumped magnetometers' registration and source localization pipeline.
    """

    def __init__(self, subject_name, opt_folder, fs_folder, opm_folder, anat_folder, trans_folder):
        self.subject_name = subject_name  # for example, OPM01
        self.opm_folder = opm_folder  # OPM data folders
        self.fs_folder = fs_folder  # freesurfer root folders
        self.opt_folder = opt_folder  # optical scanning folders
        self.anat_folfer = anat_folder  # anatomy folder (need *.nii or *.dcm)
        self.opt_and_mri_trans_folder = trans_folder
        self.subject_opm_file = None
        self.subject_fs_folder = None
        self.subject_opt_file = None
        self.trans_file = None
        self._parse_subject()

    def anatomy_preproc(self):
        """STEP 1. MRI Data(T1) Preprocessing.
        """
        # 0. check freesurfer results and run freesurfer.
        if not self.subject_fs_folder.exists() or not self.subject_fs_folder.is_dir():
            print(f"Warnning:Subject-{subject_name} 's Freesurfer Results are not exists.")

            # miss nifti file.
            # run_freesurfer(anat_file=self.subject_anat_file,subject_name=self.subject_name,
            #                recon_all=True,mkheadsurf=True)

            raise NotImplementedError
        else:
            # check surf/lh.seghead exist.
            seghead = self.subject_fs_folder / "surf" / "lh.seghead"
            if not seghead.exists() or not seghead.is_file():
                run_freesurfer(anat_file="", fs_root_dir=self.fs_folder, subject_name=self.subject_name,
                               recon_all=False, mkheadsurf=True)

        # 1. generate BEM model
        bem_path = self.subject_fs_folder / "bem"
        if not bem_path.exists() or not self.subject_fs_folder.is_dir():
            gen_bem_from_anat(subject_name=self.subject_name,
                              fs_root_dir=self.fs_folder,
                              display=False)

        # 2. get head cloud point from freesurfer
        get_face_from_anat(subject_name=self.subject_name,
                           fs_root_dir=self.fs_folder)

        # 3. you should use meshlab to manually extract the facial area,including eyes and nose parts.
        print("Anatomy preprocessing completely")
        print("Then you should use meshlab to manually extract the facial area, including eyes and nose parts!")

    def opt_preproc(self):
        """STEP2. Optical Scanning Data Preprocessing.
        """
        # check *.clean.ply file.
        # 0. First, you should extract face(nose and eyes) from *.ply(3D optical scanning data) manually.

        print("First, you should extract face(nose and eyes) from *.ply(3D optical scanning data) manually")

        print("Optical Scanning Preprocessing...")
        out_pcd = self.subject_opt_path / f"{self.subject_name}.face.trans.ply"
        trans_point_cloud_data(opt_point_cloud_filename=str(self.subject_opt_file),
                               output_point_cloud_filename=out_pcd)

        # pay attention:  you should correction manually to get *.anat.face.clean.ply
        mri_pcd = self.fs_folder / self.subject_name / f'{self.subject_name}.anat.face.clean.ply'
        trans_path = self.opt_and_mri_trans_folder / self.subject_name
        self.trans_file = get_trans_fif(opt_point_cloud_filename=out_pcd,
                                        mri_point_cloud_filename=mri_pcd,
                                        subject_name=self.subject_name,
                                        output_trans_dir=trans_path,
                                        visual_check=True)

    def source_imaging(self, method='lcmv', volume_or_surf='vol'):
        """
        Parameters
        ----------
        volume_or_surf: str (default:'surf', other option:'vol')
            - select volume source imaging or surface source imaging.
        """
        print(f"Source Imaging:{method} ,{volume_or_surf}")
        subject_name = self.subject_name
        raw_mag_fname = self.subject_opm_file
        trans_fif_fname = self.trans_file

        src_fif_fname = self.subject_fs_folder / "bem" / f"{self.subject_name}.watershed.ico4.bem.white.{volume_or_surf}.src.fif"
        bem_fif_fname = self.subject_fs_folder / "bem" / f"{self.subject_name}.watershed.ico4.bem.sol.fif"
        subjects_dir = self.fs_folder

        if method == "lcmv":
            lcmv(raw_mag_fname, trans_fif_fname,
                 src_fif_fname, bem_fif_fname,
                 subject_name, subjects_dir,
                 cache_mag_to_fif=True,
                 volume_or_surf=volume_or_surf)

    def _parse_subject(self):
        """Find the corresponding file paths(include opt\opm\fs)
           according to the subject name.
        """
        self.subject_opm_path = self.opm_folder / self.subject_name
        self.subject_opm_files = self._get_files_in_folder(self.subject_opm_path)
        self.subject_opm_file = \
        [file for file in self.subject_opm_files if "empty" not in str(file) and ".mag" in str(file)][
            0]  # remove empty opm file
        self.subject_fs_folder = self.fs_folder / self.subject_name
        self.subject_opt_path = self.opt_folder / self.subject_name
        self.subject_opt_files = self._get_files_in_folder(self.subject_opt_path)
        self.subject_opt_file = [file for file in self.subject_opt_files if "clean" in str(file)][0]

        return self.subject_opm_file, self.subject_fs_folder, self.subject_opt_file

    @staticmethod
    def _get_files_in_folder(folder_path):
        folder_path = Path(folder_path)
        if not folder_path.exists():
            print(f"Warnning:The folder {folder_path} is not exists.")
            return []
        files = [file for file in folder_path.iterdir() if file.is_file()]
        return files


if __name__ == "__main__":
    ## Main Code
    # Please run all codes from here.
    from pathlib import Path

    QM_OPM_ROOT = Path("/data/zhengli/QM_OPM/")
    subject_namelist = ['OPM01', 'OPM02', 'OPM03', 'OPM04', 'OPM05', 'OPM06']  # please note: OPM03 has some error.
    opt_folder = QM_OPM_ROOT / "Einscan"
    fs_folder = QM_OPM_ROOT / "FS_results"
    opm_folder = QM_OPM_ROOT / "OPM_Data"
    anat_folder = QM_OPM_ROOT / "T1_or_Dicom"
    trans_folder = QM_OPM_ROOT / "Trans_fif"

    for idx, subject_name in enumerate(subject_namelist):
        subject_name = 'OPM02'  # for test.
        print(f"Cnt:{idx}.Analysis Subject: {subject_name}")
        opm = OPM(subject_name, opt_folder, fs_folder, opm_folder, anat_folder, trans_folder)
        print(opm._parse_subject())

        ## Step 1. Anatomy Part
        # Generate surface data for registration based on T1 images, including only
        # the eyes and nose parts.
        # Note：Requires manual cutting correction.
        #      - get {subject_name}.anat.face.clean.ply
        opm.anatomy_preproc()

        ## Step 2. Optical Scanning Part
        # Generate surface data(point cloud data) for registration based on 3D Optical Scanning,
        # including only the eyes and nose parts.
        # Note: Requires manual cutting correction.
        #      - get {subject_name}.face.clean.ply
        opm.opt_preproc()

        ## Step 3. Source Imaging Part
        opm.source_imaging(method="lcmv", volume_or_surf='surf')  # or surf



