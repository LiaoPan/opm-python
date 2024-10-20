# -*- coding: utf-8 -*-
#author:
# - XuWei, initialize 
# - LiaoPan, Integration
"""
Anatomy Data Preprocessing.
"""

import mne
import subprocess
import mne.bem
import numpy as np
from pathlib import Path



def gen_bem_from_anat(subject_name,fs_root_dir,display=False):
    """
    Generate BEM model based on Freesurfer Results.

    Parameters
    ----------
    subject_name:str
        - the name of subject
    fs_root_dir:str
        - the directory where the freesurfer results are saved, just like SUBJECTS_DIR environment variable.
    display:bool
        - If True, display with GUI.
    """

    subj_head = fs_root_dir / subject_name
    bem_path = subj_head / 'bem'
    bem_path.mkdir(parents=True, exist_ok=True)

    fname_bem_surf = bem_path / f'{subject_name}.watershed.ico4.bem.fif'
    fname_bem_sol = bem_path / f'{subject_name}.watershed.ico4.bem.sol.fif'

    mne.bem.make_watershed_bem(subject=subject_name, subjects_dir=fs_root_dir, overwrite=True, volume='T1', atlas=True, gcaatlas=False, show=False, copy=True)
    bem_surf = mne.make_bem_model(subject=subject_name, subjects_dir=fs_root_dir, ico=4, conductivity=(0.3, 0.006, 0.3))
    bem_sol = mne.make_bem_solution(surfs=bem_surf)

    mne.write_bem_surfaces(fname_bem_surf, bem_surf, overwrite=True)
    mne.write_bem_solution(fname=fname_bem_sol, bem=bem_sol, overwrite=True)

    for surface_name in ['pial', 'white']:
        fname_src_spac = bem_path / f'{subject_name}.watershed.ico4.bem.{surface_name}.surf.src.fif'
        fname_vol_src_spac = bem_path / f'{subject_name}.watershed.ico4.bem.{surface_name}.vol.src.fif'
        src_spac = mne.setup_source_space(subject=subject_name, subjects_dir=fs_root_dir, spacing='ico4', surface=surface_name, add_dist=False)
        vol_src_spac = mne.setup_volume_source_space(subject=subject_name, subjects_dir=fs_root_dir, surface=fs_root_dir / subject_name / 'bem' / 'inner_skull.surf', verbose=True)
        mne.write_source_spaces(fname_src_spac, src_spac, overwrite=True)
        mne.write_source_spaces(fname_vol_src_spac, vol_src_spac, overwrite=True)

    if display:
        plot_bem_kwargs = dict(subject=subject_name, subjects_dir=subjects_dir, brain_surfaces='white', orientation='coronal', slices=[50, 100, 150, 200])
        mne.viz.plot_bem(**plot_bem_kwargs)  # type: ignore


def get_face_from_anat(subject_name,fs_root_dir):
    """
    Read head surface from FreeSurfer.
    Parameters
    ----------
    subject_name:str
        - the name of subject
    fs_root_dir:str
        - the directory where the freesurfer results are saved, just like SUBJECTS_DIR environment variable.
    """
    head_surface = mne.read_surface(fs_root_dir / subject_name / 'surf' / 'lh.seghead')
    np.savetxt(fs_root_dir / subject_name /f'{subject_name}.face.ManualExtractRequired.txt', head_surface[0])  # type: ignore
    

def run_freesurfer(anat_file,fs_root_dir,subject_name,recon_all=True,mkheadsurf=True):
    """
    Run freesurfer
    Parameters
    ---------
    anat_file:str
        the filename of anatomy.(T1.nii.gz)
    fs_root_dir:str
        the directory where the freesurfer results are saved
    subject_name:str
        the subject name for saving fs results.
    """
    subj = subject_name
    commanda = f"recon-all -all -i {anat_file} -s {subj}"
    commandb = f"recon-all -all -s {subj} -3T -openmp 4"
    commandc = f"export SUBJECTS_DIR={fs_root_dir};mkheadsurf -s {subj} -srcvol T1.mgz -thresh1 30"
    if recon_all:
        print("Recon_all...")
        command = commanda+";"+commandb
        print(f"commad:{command}")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print("Output:", output.decode())
        if error:
            print("Error:", error.decode())
    if mkheadsurf:
        print("MKHeadSurfer: segment and create a surface representation of the head...")
        print(f"commad:{commandc}")
        process = subprocess.Popen(commandc, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print("Output:", output.decode())
        if error:
            print("Error:", error.decode())
