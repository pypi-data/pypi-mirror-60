# Accelerometer Feature Extractor (AFE) #

This library is used to extract features from accelerometer data.  Features include e.g. frequency of motion, mean acceleration (vector magnitude), etc.  The features are meant to be useful to classify activity type, disease state, or whatever labels you have for your accelerometer data.

### How do I get set up? ###

You will need Python 3 with `numpy`, `scipy`, and `pandas`.

You will also need one of my other libraries, `actigraph`, which is also in PyPI.  However, that library is only used to compute one feature, and you could safely remove the dependency from `features.py` if you didn't want to use it.

To install from PyPI:

    pip3 install afe

Or from git:

    git clone https://bitbucket.org/atpage/afe.git
    cd afe
    pip3 install -e .

### How do I run it? ###

First, create a pandas DataFrame containing your accelerometer samples.  The index should be time (as either a timestamp, or number of seconds), and the columns should be named `x`, `y`, and `z`.  If you have gyroscope data as well, include those columns as `rx`, `ry`, and `rz`.  Any axis can be omitted if your hardware didn't include it.  Then:

    # my data is already stored in df
    
    from afe import AFE
    afe = AFE(df)
    features = afe.get_features(window_size=60, overlap=0)
    
    # features is a new DataFrame with a row for each 60-second window, and a column for each feature.

### Who do I talk to? ###

* Alex Page, alex.page@rochester.edu
