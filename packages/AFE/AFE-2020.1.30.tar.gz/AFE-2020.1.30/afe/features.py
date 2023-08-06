
import datetime as dt

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.stats import entropy

from actigraph import raw_to_counts

# TODO: convert Datetime->Float or vice versa to speed up computation

############################## Helper functions: ###############################

def get_starts_ends(data, epochs, window_size):
    # could use window+overlap instead of passing epochs.
    if type(data.index) == pd.DatetimeIndex:
        epoch_starts = epochs.index.to_pydatetime()
        epoch_ends = epoch_starts + dt.timedelta(seconds=window_size)
    elif type(data.index) == pd.Float64Index:
        epoch_starts = epochs.index.values
        epoch_ends = epoch_starts + window_size
    return epoch_starts, epoch_ends

def get_peaks_from_fft(yf, xf):
    """yf is the fft amplitude.  xf are the corresponding frequencies. returns
    (frequencies, heights)"""
    # Find peaks:
    prom = np.percentile(yf, 95)
    peaks, peak_props = find_peaks(yf, prominence=prom, height=(None,None))
    # Arrange by prominence:
    order = np.flip(np.argsort(peak_props['prominences']))
    freqs = xf[peaks[order]]
    heights = peak_props['prominences'][order]
    return freqs, heights

def get_sr(df):
    """Returns the sample rate in Hz for the given data.  May not work if SR isn't
    constant."""
    if len(df) < 2:
        raise ValueError("dataset must have >= 2 samples to find SR.")
    if type(df.index) == pd.DatetimeIndex:
        return 1/(df.index[1]-df.index[0]).total_seconds()
        # TODO: make a median method for this, rather than first 2 elements?
    elif type(df.index) == pd.Float64Index:
        #return 1/(df.index[1]-df.index[0])
        return 1.0/np.median(df.index.values[1:] - df.index.values[:-1])

def get_freq_stats(frame, **kwargs):
    """Find the most dominant frequencies (Hz) in VM acceleration between some start
    and stop times.  Peaks outside [fmin,fmax] are ignored.  The list is sorted
    by prominence.  Peak prominence must be >95th percentile of signal
    amplitudes to make the list.  Returns a dict containing freqs, peak heights,
    total power, power spectral entropy, f_625, and p_625.  If no peaks are
    found, peaks and heights are empty.

    Keyword arguments:
    frame -- a (slice of a) DataFrame
    sr    -- sample rate (Hz)
    fmin  -- minumum frequency to include (Hz)
    fmax  -- maximum frequency to include (Hz)
    """
    sr = kwargs.get('sr')
    if not sr:
        sr = get_sr(frame)
    fmin  = kwargs.get('fmin', 0.2)  # TODO: 0.1 default?
    fmax  = kwargs.get('fmax', 5)
    if (fmin > 0.6) or (fmax < 2.5):
        raise ValueError("[fmin, fmax] must include the range [0.6, 2.5] (Hz)")
    accel = frame.vm
    # Compute FFT:
    yf = np.abs(np.fft.rfft(accel))  # TODO?: might phase data be useful?
    xf = np.fft.rfftfreq( len(accel), 1.0/sr )
    freq_bin_width = xf[1]  # minus xf[0], which is 0
    # TODO?: 'friendly' window sizes for FFT performance
    # Crop to different frequency ranges:
    i625  = (xf > 0.6)  & (xf < 2.5)
    yf625 = yf[i625]
    xf625 = xf[i625]
    i     = (xf > fmin) & (xf < fmax)
    yf    = yf[i]
    xf    = xf[i]
    # Find peaks:
    freqs, heights = get_peaks_from_fft(yf, xf)
    # Other stats:
    ent = entropy(yf**2)
    total_power = np.sum((yf/sr)**2) * freq_bin_width
    # total power is only within this restricted frequency range (0.2-5Hz;
    # reference uses 0.3-15Hz).  units are ~ W/kg not W.  to get total power
    # over all freqs, we don't need FFT, could just do np.sum(accel**2) / sr.
    peak_625_loc = np.argmax(yf625)
    return {
        'top_freqs': freqs,
        'top_freq_powers': (heights/sr)**2 * freq_bin_width,
        'total_power': total_power,
        'entropy': ent,
        # TODO: use get_peaks_from_fft() for f_625+p_625 if there is a minimum
        # power requirement for them to be defined.
        'f_625': xf625[peak_625_loc],
        'p_625': (yf625[peak_625_loc]/sr)**2 * freq_bin_width,
    }

######################### Feature-computing functions: #########################

def vm_accel(**kwargs):
    """kwargs:
       - data (the dataframe)
       - epochs
       - window_size
       - overlap
       - include_timestamp_features?
    """
    data = kwargs.get('data')
    epochs = kwargs.get('epochs')
    window_size = kwargs.get('window_size')
    overlap = kwargs.get('overlap')
    if overlap == 0:
        if type(data.index) == pd.DatetimeIndex:
            groups = data.groupby(
                (data.index - data.index[0]).total_seconds() // window_size
            )
        elif type(data.index) == pd.Float64Index:
            groups = data.groupby(
                (data.index - data.index[0]) // window_size
            )
        epochs['vm_mean'] = groups.mean().vm.values
        epochs['vm_std']  = groups.std().vm.values
    else:
        # can't use groupby() etc. with overlapping windows.  see
        # https://github.com/pandas-dev/pandas/issues/15354.
        vm_mean = np.full(len(epochs), np.nan, dtype=np.float64)
        vm_std  = np.full(len(epochs), np.nan, dtype=np.float64)
        epoch_starts, epoch_ends = get_starts_ends(data, epochs, window_size)
        for i, (epoch_start, epoch_end) in enumerate(zip(epoch_starts, epoch_ends)):
            accel = data.loc[epoch_start:epoch_end]
            vm_mean[i] = np.mean(accel.vm)
            vm_std[i]  = np.std(accel.vm)
        epochs['vm_mean'] = vm_mean
        epochs['vm_std']  = vm_std

def freq_stats(**kwargs):
    """Gets dominant frequencies, power, entropy, etc."""
    data = kwargs.get('data')
    epochs = kwargs.get('epochs')
    window_size = kwargs.get('window_size')
    epoch_starts, epoch_ends = get_starts_ends(data, epochs, window_size)
    f1          = np.full(len(epochs), np.nan, dtype=np.float64)
    p1          = np.full(len(epochs), np.nan, dtype=np.float64)
    f2          = np.full(len(epochs), np.nan, dtype=np.float64)
    p2          = np.full(len(epochs), np.nan, dtype=np.float64)
    f625        = np.full(len(epochs), np.nan, dtype=np.float64)
    p625        = np.full(len(epochs), np.nan, dtype=np.float64)
    total_power = np.full(len(epochs), np.nan, dtype=np.float64)
    ps_ent      = np.full(len(epochs), np.nan, dtype=np.float64)
    for i, (epoch_start, epoch_end) in enumerate(zip(epoch_starts, epoch_ends)):
        frame = data[epoch_start:epoch_end]
        results = get_freq_stats(frame, **kwargs)  # TODO... fmin, fmax
        if len(results['top_freqs']) >= 1:
            f1[i] = results['top_freqs'][0]
            p1[i] = results['top_freq_powers'][0]
        if len(results['top_freqs']) >= 2:
            f2[i] = results['top_freqs'][1]
            p2[i] = results['top_freq_powers'][1]
        f625[i] = results['f_625']
        p625[i] = results['p_625']
        total_power[i] = results['total_power']
        ps_ent[i] = results['entropy']
        # Note: reference uses 0.3-15Hz total power.  We use 0.2-5Hz.
    f1_prev = np.concatenate(([np.nan],f1[:-1]))
    # TODO: standardize these output names:
    epochs['f1_Hz']       = f1
    epochs['f1_power']    = p1
    epochs['f1_change']   = f1 / f1_prev  # could do this in db instead, but meh.
    epochs['f2_Hz']       = f2
    epochs['f2_power']    = p2
    epochs['f625_Hz']     = f625
    epochs['f625_power']  = p625
    epochs['total_power'] = total_power
    epochs['p1_fraction'] = epochs['f1_power'] / epochs['total_power']
    epochs['ps_entropy']  = ps_ent

def corr_coeffs(**kwargs):
    data = kwargs.get('data')
    epochs = kwargs.get('epochs')
    window_size = kwargs.get('window_size')
    epoch_starts, epoch_ends = get_starts_ends(data, epochs, window_size)
    corr_xy = np.full(len(epochs), np.nan, dtype=np.float64)
    corr_xz = np.full(len(epochs), np.nan, dtype=np.float64)
    corr_yz = np.full(len(epochs), np.nan, dtype=np.float64)
    for i, (epoch_start, epoch_end) in enumerate(zip(epoch_starts, epoch_ends)):
        accel = data.loc[epoch_start:epoch_end]
        axes = [ax for ax in ['x','y','z'] if ax in accel.columns]
        corrs = np.corrcoef(accel[axes].T)
        if 'x' in accel.columns and 'y' in accel.columns:
            corr_xy[i] = corrs[axes.index('x')][axes.index('y')]
        if 'x' in accel.columns and 'z' in accel.columns:
            corr_xz[i] = corrs[axes.index('x')][axes.index('z')]
        if 'y' in accel.columns and 'z' in accel.columns:
            corr_yz[i] = corrs[axes.index('y')][axes.index('z')]
    epochs['corr_xy'] = corr_xy
    epochs['corr_xz'] = corr_xz
    epochs['corr_yz'] = corr_yz

def acti_counts(**kwargs):
    """Compute Actigraph-like "counts".  See
    https://www.ncbi.nlm.nih.gov/pubmed/28604558.

    See also:
    https://actigraph.desk.com/customer/en/portal/articles/2515835-what-is-the-difference-among-the-energy-expenditure-algorithms-
    https://actigraph.desk.com/customer/en/portal/articles/2515804-what-is-the-difference-among-the-met-algorithms-
    Maybe this when we start getting HR data:
    https://actigraph.desk.com/customer/en/portal/articles/2515579-what-is-hree-in-actilife-
    """
    data        = kwargs.get('data')
    epochs      = kwargs.get('epochs')
    overlap     = kwargs.get('overlap')
    window_size = kwargs.get('window_size')
    sr          = kwargs.get('sr')
    if not sr:
        sr = get_sr(data)
    # TODO: missing axes
    xc = raw_to_counts(data['x'],sr)
    yc = raw_to_counts(data['y'],sr)
    zc = raw_to_counts(data['z'],sr)
    vmc = np.sqrt(xc**2 + yc**2 + zc**2)
    # those countain the number of counts for each second of data
    if type(data.index) == pd.DatetimeIndex:
        index = pd.date_range(
            freq = '1S',
            start = data.index[0] + dt.timedelta(seconds = 0.5),
            periods = len(vmc),
            name = 'time'
        )
    elif type(data.index) == pd.Float64Index:
        index = pd.Float64Index(
            data = np.arange(data.index[0]+0.5, data.index[-1]+0.5, 1),
            name = 'time'
        )
    counts = pd.Series(
        data = vmc,
        index = index,
        dtype = np.float64,
        name = 'counts_per_sec'
    )
    # note: with 0.5s offset, counts happen *around* reported time, not just
    # before or after it
    if overlap == 0:
        counts = counts.to_frame()
        counts['elapsed_sec'] = counts.index - data.index[0]
        if type(data.index) == pd.DatetimeIndex:
            counts['elapsed_sec'] = counts['elapsed_sec'].total_seconds()
        counts_groups = counts.groupby(counts.elapsed_sec // window_size).counts_per_sec
        epochs['cpm_mean'] = counts_groups.sum().values / (window_size/60.0)
    else:
        cpm_mean = np.full(len(epochs), np.nan, dtype=np.float64)
        epoch_starts, epoch_ends = get_starts_ends(data, epochs, window_size)
        for i, (epoch_start, epoch_end) in enumerate(zip(epoch_starts, epoch_ends)):
            accel = data.loc[epoch_start:epoch_end]
            cpm_mean[i] = np.sum(counts[epoch_start:epoch_end]) / (window_size/60.0)
        epochs['cpm_mean'] = cpm_mean

################# Map functions to the features they compute: ##################

function_feature_map = {

    vm_accel:    ['vm_mean', 'vm_std'],

    freq_stats:  ['f1_Hz', 'f1_power', 'f1_change', 'f2_Hz', 'f2_power',
                  'f625_Hz', 'f625_power', 'total_power', 'p1_fraction', 'ps_entropy'],

    corr_coeffs: ['corr_xy', 'corr_xz', 'corr_yz'],

    acti_counts: ['cpm_mean'],

}

################################################################################
