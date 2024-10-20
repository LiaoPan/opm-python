# -*- coding: utf-8 -*-
# author:
# - XuWei, for Initi Version
# - LiaoPan, for Integration
import mne
import numpy as np
from opmpy.mag import opmag2fif
from mne.beamformer import make_lcmv, apply_lcmv


def lcmv(raw_mag_fname, trans_fif_fname, src_fif_fname, bem_fif_fname, subject_name, subjects_dir,
         cache_mag_to_fif=True, visualization=False, volume_or_surf='vol'):
    # raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose=False)
    if cache_mag_to_fif:  # save mag file into fif file, speed up reading.
        fif_fname = raw_mag_fname.parent / f"{raw_mag_fname.stem}.fif"
        if not fif_fname.exists() or not fif_fname.is_file():
            opmag2fif(raw_mag_fname, fif_fname)
        raw = mne.io.read_raw_fif(fif_fname, preload=True, verbose=False)
    else:
        raw = opmag2fif(raw_mag_fname, return_raw=True)

    raw.notch_filter(freqs=np.arange(50, 301, 50), n_jobs=8, verbose=False)
    raw.filter(l_freq=0.1, h_freq=40.0, n_jobs=8, verbose=False)

    events = mne.find_events(raw, stim_channel='STI101', verbose=False)
    events[:, 0] = events[:, 0] + 50  # pay attenion here! add delay
    epochs = mne.Epochs(raw, events, tmin=-0.2, tmax=1.0, preload=True, detrend=1, proj=False, verbose=False)
    epochs.apply_baseline((-0.2, 0))

    # visulize
    if visualization:
        epochs.plot(block=True)

    evoked = epochs.average()

    data_cov = mne.compute_covariance(epochs, tmin=0.01, tmax=0.80, method='empirical')
    noise_cov = mne.compute_covariance(epochs, tmin=-0.2, tmax=0, method='empirical')

    del raw

    # visualize
    if visualization:
        mne.viz.plot_sensors(epochs.info, kind='topomap', show_names=True, block=True)

    # coregistraion visualization.
    if visualization:
        mne.gui.coregistration(subjects_dir=subjects_dir, block=True)

    fwd = mne.make_forward_solution(evoked.info,  # type: ignore
                                    trans=trans_fif_fname,
                                    src=src_fif_fname,
                                    bem=bem_fif_fname,
                                    meg=True, eeg=False, n_jobs=10, verbose=False)

    filters = make_lcmv(evoked.info, fwd, data_cov, reg=0.05, noise_cov=noise_cov, pick_ori='max-power',
                        weight_norm='unit-noise-gain', rank=None)  # type: ignore

    stc = apply_lcmv(evoked, filters)

    if volume_or_surf == 'surf':
        brain_mag = stc.plot(clim='auto', src=fwd['src'], subject=subject_name, subjects_dir=subjects_dir,
                             initial_time=0.1, verbose=True,
                             brain_kwargs=dict(block=True))  # type: ignore
        brain_mag.add_text(0.1, 0.9, "LCMV", "title", font_size=14)
    elif volume_or_surf == 'vol':
        brain_mag = stc.plot(clim='auto', src=fwd['src'], subject=subject_name, subjects_dir=subjects_dir,
                             initial_time=0.1, verbose=True)
        print("brain_mag:", brain_mag)
