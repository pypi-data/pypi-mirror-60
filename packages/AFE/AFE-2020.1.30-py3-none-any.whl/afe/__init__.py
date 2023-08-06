
import pandas as pd
import numpy as np
from math import ceil

from .features import function_feature_map

class AFE:
    """Accelerometer Feature Extractor.  Extracts features useful for machine
    learning from raw accelerometer/gyroscope data."""

    def __init__(self, data, sr=None):
        """data is a pandas DataFrame containing a time-based index (either timestamp,
        or seconds elapsed).  Columns must be labeled x, y, z (for
        accelerometer) and rx, ry, rz (for gyroscope).  Units must be g's.  Any
        columns may be omitted, e.g. a 2-axis accelerometer may include only x and
        y.  You shouldn't normally need to specify sample rate (sr).
        """
        if type(data) == pd.DataFrame:
            check_timeindex(data)
            self.data = data
        else:
            raise TypeError("data must be a Pandas DataFrame.")
        self.sr = sr

    def compute_vm_accel(self, overwrite=False):
        if 'vm' not in self.data.columns or overwrite:
            vm = np.zeros(len(self.data))
            for axis in ['x','y','z']:
                if axis in self.data.columns:
                    vm = vm + self.data[axis].values**2
            self.data['vm'] = np.sqrt(vm.astype(np.float64))

    def get_features(self, window_size=30, overlap=0, include_timestamp_features=False,
                     include_features=[], exclude_features=[]):
        """Get a DataFrame of features.  Data will be segmented into window_size-second
        windows with overlap-second overlaps.  Set window_size and overlap to
        None to extract 1 set of features for the entire dataset.

        If include_timestamp_features is True, and the dataset has a timestamp
        index, features such as day_of_week will be included in the returned
        DataFrame.  This may be useful to make predictions that have seasonal,
        circadian, or other time-dependence.

        include_features and exclude_features are whitelist/blacklist (list of
        strings) of features to be computed.  If a feature extraction function
        provides some features that are not blacklisted, but some that are, it
        will be run anyway.
        """
        # TODO: instead of include_timestamp_features being bool, specify
        # allowed list of them.  e.g. ['hour', 'day'] means include hour of day
        # and day of week.

        # TODO: implement some kind of save/don't-recompute option that
        # preserves already-computed features internally and can recall them
        # without recomputing.

        if overlap >= window_size:
            raise ValueError("overlap must be less than window size.")

        # TODO: support negative overlap to allow gaps (if it doesn't work already)

        if include_features:
            functions_to_run = [fn for fn in function_feature_map if not set(function_feature_map[fn]).isdisjoint(set(include_features))]
        else:
            functions_to_run = list(function_feature_map.keys())
        if exclude_features:
            functions_to_run = [fn for fn in functions_to_run if not set(function_feature_map[fn]).issubset(set(exclude_features))]

        start_times = get_epoch_start_times(self.data, window_size, overlap)
        epochs = pd.DataFrame(data=None, index=start_times,
                              columns=None, dtype=None)

        # could store one of these instead of passing window and overlap around separately from epochs:
        # epochs.window_size = window_size
        # epochs.window_overlap = overlap

        self.compute_vm_accel()
        for function in functions_to_run:
            function(
                data = self.data,
                epochs = epochs,  # function will modify this in place.  at least that's the plan right now.
                window_size = window_size,
                overlap = overlap,
                include_timestamp_features = include_timestamp_features,
                sr = self.sr,
            )

        # TODO?: remove features that were excluded (or not included) from df before returning
        return epochs

def check_timeindex(df):
    """Make sure the DataFrame's index is either float or timestamp.
    """
    if type(df.index) == pd.DatetimeIndex or type(df.index) == pd.Float64Index:
        return
    raise TypeError("data index must be float or timestamp.")

def get_epoch_start_times(data, window_size, overlap):
    """Get the start times for all epochs in this recording (as a pandas Index)."""
    period = window_size - overlap
    if type(data.index) == pd.DatetimeIndex:
        start_times = pd.date_range( start = data.index[0],
                                     end   = data.index[-1],
                                     freq  = '%dS'%period,
                                     name  = 'epoch_start' )
    elif type(data.index) == pd.Float64Index:
        timespan = data.index[-1] - data.index[0]
        windows = ceil(timespan / window_size)
        start_times = [data.index[0] + i*period for i in range(windows)]
        start_times = pd.Float64Index(start_times, name = 'epoch_start')
    return start_times
