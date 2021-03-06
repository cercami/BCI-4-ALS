"""
Preprocessing of EEG data

The function planned to be stand-alone to be able to preprocessing multiple
subjects in easy way.
"""

import mne
import matplotlib.pyplot as plt
import pyxdf
import pandas as pd
import numpy as np


data_params = {
    'path': 'EEG.xdf',
    'channel_names': ['Fp1', 'Fp2', 'C03', 'C04', 'P07', 'P08', 'O01', 'O02',
                      'F07', 'F08', 'F03', 'F04', 'T07', 'T08', 'P03'],
    'sample_freq': None
}

filter_params = {
    'low_pass': 40,
    'high_pass': 0.5,
}


def get_eeg_data(path):

    """
    Get the raw EEG data
    :return:
    """

    # Get the xdf file
    data, header = pyxdf.load_xdf(path, [{'type': 'EEG'}])

    # Get the EEG data

    eeg_data = data[0]['time_series']  # get the data
    data_params['sample_freq'] = int(data[0]['info']['nominal_srate'][0])  # update the sample rate

    # Remove the first channel
    eeg_data = np.delete(eeg_data, obj=0, axis=1)

    # Debug print
    print('EEG data loaded\nData shape: {}'.format(eeg_data.shape))

    return eeg_data


def filter_eeg_data(eeg, sample_freq, params):

    """
    All the filtering part will be in this function
    :param params: parameters for the filtering part
    :param sample_freq: sample frequency of the data
    :param eeg: ndarray of the original EEG data
    :return: ndarray of the filtered EEG data
    """

    # Params
    low_pass = params['low_pass']
    high_pass = params['high_pass']

    # Convert to float64 in order to fit mne functions
    eeg = eeg.astype(np.float64)
    eeg = eeg.T  # mne functions look for the channels as rows

    # Low-pass filter
    eeg = mne.filter.filter_data(eeg, l_freq=None, h_freq=low_pass, sfreq=sample_freq)

    # High-pass filter
    eeg = mne.filter.filter_data(eeg, l_freq=high_pass, h_freq=None, sfreq=sample_freq)

    # Notch filter wasn't added because I didn't understand the Matlab `pop_basicfilter` args

    return eeg.T


def save_cleaned_eeg(eeg, channel_names, path):

    """
    Save the cleaned EEG file after adding the channel names into the file.
    The cleaned file save in the same path but with `cleaned` added to his name.
    :param channel_names: list of channel names
    :param eeg: EEG ndarray
    :param path: path of the original file (str)
    :return:
    """

    # Add channel names
    cleaned_eeg = pd.DataFrame(data=eeg, columns=channel_names)

    # Create the output path
    output_path = path.split('.')[0] + '_cleaned.csv'

    # Output the cleaned EEG
    cleaned_eeg.to_csv(output_path, index=False)


def main():

    # Load the EEG data
    eeg = get_eeg_data(path=data_params['path'])

    # Filter the data
    eeg = filter_eeg_data(eeg, data_params['sample_freq'], filter_params)

    # Save the filtered EEG
    save_cleaned_eeg(eeg, data_params['channel_names'], data_params['path'])


if __name__ == '__main__':

    main()


