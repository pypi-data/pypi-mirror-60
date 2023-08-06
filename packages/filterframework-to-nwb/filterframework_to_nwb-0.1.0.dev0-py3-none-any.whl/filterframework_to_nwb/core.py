
# General dependencies
import os
# Time
from datetime import datetime
from logging import getLogger

import numpy as np
import pynwb
import scipy.interpolate as interpolate
from dateutil import tz

import filterframework_to_nwb.fl_extension_helpers as flh
# # Helpers for parsing Frank Lab Matlab data
import filterframework_to_nwb.nspike_helpers as ns
# Frank Lab PyNWB extensions and extension-related helpers
import franklab_nwb_extensions.fl_extension as fle

# Recording parameters needed for import:
LFP_SAMPLING_RATE = 1500.0  # Hz

# Conversion: data are in uV, divide by 1e6 to get to volts:
MICROVOLTS_TO_VOLTS = 1.0 / 1e6

# Nspike time conversion
NSPIKE_TIMESTAMPS_PER_SECOND = 10000

logger = getLogger(__name__)


def write_ephys(nwbf, data_dir, animal_prefix, day, recording_device):
    '''create the ElectrodeGroups, Electrodes, Unit and LFP data structures

    Parameters
    ----------
    nwbf : pynwb.NWBFile instance
    data_dir : str
    animal_prefix : str
    day : int
    recording_device : str

    '''

    # Parse tetrodes metadata from the  Frank Lab Matlab files
    tetrode_metadata = ns.parse_franklab_tetrodes(data_dir, animal_prefix, day)

    # Four channels per tetrode by definition
    num_chan_per_tetrode = 4

    # Initialize dictionaries to store the metadata
    tet_electrode_group = {}  # group for each tetrode
    tet_electrode_table_region = {}  # region for each tetrode (all channels)
    lfp_electrode_table_region = {}  # region for each tetrode's LFP channels

    chan_num = 0  # Incrementing channel number
    lfp_channels = list()
    for tet_num, tet in tetrode_metadata.items():
        # Define some metadata parameters
        tetrode_name = f"{tet_num:03d}"
        impedance = np.nan
        filtering = 'unknown - likely 600Hz-6KHz'
        location = ns.get_franklab_tet_location(
            tet)  # area/subarea in the brain
        depth = ns.get_franklab_tet_depth(tet)  # depth in the brain
        description = f"tetrode {tet_num} located in {location} on day {day}"

        # 1. Represent the tetrode in NWB as an ElectrodeGroup
        tet_electrode_group[tet_num] = nwbf.create_electrode_group(
            name=tetrode_name,
            description=description,
            location=location,
            device=recording_device)

        # 2. Represent each channels of the tetrode as a row in the
        # NWBFile.electrodes table. We do not have x and y coordinates for
        # electrodes, so we set to np.nan.
        for i in range(num_chan_per_tetrode):
            nwbf.add_electrode(x=np.nan,
                               y=np.nan,
                               z=depth,
                               imp=impedance,
                               location=location,
                               filtering=filtering,
                               # tetrode this electrode belongs to
                               group=tet_electrode_group[tet_num],
                               group_name=tet_electrode_group[tet_num].name,
                               id=chan_num)
            chan_num = chan_num + 1  # number of channels processed so far

        # 3. Create an Electrode Table Region (slice into the electrodes table)
        # for each tetrode
        table_region_description = f'tetrode {tet_num} all channels'
        table_region_name = f'{tet_num}'
        # rows of NWBFile.electrodes table
        table_region_rows = list(
            range(chan_num - num_chan_per_tetrode, chan_num))
        tet_electrode_table_region[tet_num] = nwbf.create_electrode_table_region(  # noqa
            region=table_region_rows,
            description=table_region_description,
            name=table_region_name)

        # 4. Create an ElectrodeTableRegion for all LFP recordings
        # Assume that LFP is taken from the first channel
        lfp_channels.append(chan_num - num_chan_per_tetrode)

    table_region_description = 'tetrode LFP channels'
    lfp_electrode_table_region = nwbf.create_electrode_table_region(
        region=lfp_channels,
        description=table_region_description,
        name='electrodes')

    # Get a list of all the LFP files
    # look in a subdirectory called EEG
    eeg_path = os.path.join(data_dir, 'EEG')
    eeg_files = ns.get_eeg_by_day(eeg_path, animal_prefix.lower(), 'eeg')
    if len(eeg_files) == 0:
        # try without the lower()
        eeg_files = ns.get_eeg_by_day(eeg_path, animal_prefix, 'eeg')

    # Intialize a new ecephys.LFP object to store LFP from all of our tetrodes.
    lfp = pynwb.ecephys.LFP()

    ""
    # we will read in all of the timestamps and data and then combine things
    # into a single timestamps vector and a single 2D data array
    timestamps = dict()
    data = dict()
    start_time = 0
    end_time = 1e100
    for tet_num in tetrode_metadata.keys():
        # Give a unique name to this tetrode's LFP data
        lfp_name = "{prefix}lfp-{day}".format(
            prefix=animal_prefix.lower(), day=day)

        # Parse the LFP from Frank Lab Matlab files. timestamps and data will
        # be lists of times / data points, one list per epoch
        timestamps[tet_num], data[tet_num] = ns.build_day_eeg(
            eeg_files[day][tet_num], LFP_SAMPLING_RATE)

    # put all of the LFP data on a common time base by truncating and
    # interpolating where necessary
    first_tet = list(tetrode_metadata.keys())[0]
    num_epochs = len(timestamps[first_tet])

    start_time = np.zeros((num_epochs, 1))
    end_time = np.zeros((num_epochs, 1))
    end_time[:] = 1e100

    for epoch in range(num_epochs):
        # find the times for each epoch
        for tet_num in timestamps.keys():
            # if the current start time is before the first timestamp, reset it
            # to the first timestamp
            if start_time[epoch] < timestamps[tet_num][epoch][0]:
                start_time[epoch] = timestamps[tet_num][epoch][0]
            # if the current end time is after the last timestamp, reset it to
            # the first timestamp
            if end_time[epoch] > timestamps[tet_num][epoch][-1]:
                end_time[epoch] = timestamps[tet_num][epoch][-1]

    # Given that list of start and end times, we can go through each epoch and
    # interpolate the data to the new times
    final_times = np.zeros((0,), np.float64)
    final_data = np.zeros((len(timestamps.keys()), 0), np.int16)

    for epoch in range(num_epochs):
        times = np.arange(start_time[epoch],
                          end_time[epoch], 1 / LFP_SAMPLING_RATE)
        # this allows for sample times past end_time[epoch], so we need to
        # test for that and delete the final element in that case
        if times[-1] > end_time[epoch]:
            times = times[0:-2]
        # interpolate across the data for the new times
        data_matrix = np.empty([len(data.keys()), len(times)], dtype=np.int16)
        index = 0
        for tet_num in timestamps.keys():
            datafn = interpolate.interp1d(
                timestamps[tet_num][epoch], data[tet_num][epoch], kind='cubic')
            data_matrix[index] = np.round(datafn(times))
            index += 1
        final_times = np.concatenate((final_times, times))
        final_data = np.concatenate((final_data, data_matrix), axis=1)

    # Add LFP as a new ElectricalSeries in the ecephys.LFP object
    lfp.create_electrical_series(name=lfp_name,
                                 data=final_data,
                                 conversion=MICROVOLTS_TO_VOLTS,
                                 electrodes=lfp_electrode_table_region,
                                 timestamps=final_times)

    # Add the ecephys.LFP object to the NWBFile
    nwbf.add_acquisition(lfp)

    # SINGLE UNITS
    # Constants for processing spikes
    timestamps_column = 0  # index of the timestamps column in the units table

    # ------------
    # Add some metadata columns to the NWBFile.units table
    # ------------
    nwbf.add_unit_column(
        'cluster_name', 'cluster name from clustering software')
    nwbf.add_unit_column('sorting_metric', 'a sorting metric for this unit')

    # ------------
    # Load spiking data into a dictionary ordered by
    # [tetrode num][cluster num][epoch]
    # ------------
    spiking_data = ns.parse_franklab_spiking_data(data_dir, animal_prefix, day)

    # ------------
    # Add each cluster to the NWBFile.units table, concatenating the data
    # across epochs
    # and keeping track of observation intervals
    # ------------
    cluster_id = 0  # increment for each cluster we process
    for tet_num in spiking_data.keys():
        for cluster_num in spiking_data[tet_num].keys():

            # Collect spike times and obs intervals for every epoch in this
            # cluster dictionary indexed by epoch
            cluster_spikes = spiking_data[tet_num][cluster_num]
            spike_times_each_epoch = []
            obs_int_each_epoch = np.zeros([0, 2])
            for epoch in cluster_spikes.keys():
                # Get this cluster's spikes for this epoch
                if cluster_spikes[epoch]['data'].shape[0]:
                    epoch_data = cluster_spikes[
                        epoch]['data'][:, timestamps_column]
                    spike_times_each_epoch.append(
                        epoch_data + nwbf.session_start_time.timestamp())
                # Get this cluster's observation intervals for this epoch
                for epoch_obs_int in cluster_spikes[epoch]['timerange']:
                    # Convert from Nspike timestamps to POSIX time
                    epoch_obs_int = (epoch_obs_int.T.astype(
                        float) / NSPIKE_TIMESTAMPS_PER_SECOND +
                        nwbf.session_start_time.timestamp())
                    obs_int_each_epoch = np.append(
                        obs_int_each_epoch, [epoch_obs_int], axis=0)

            # Concatenate the spiketimes across epochs.
            spiketimes = np.concatenate(spike_times_each_epoch)

            # Add this cluster to the NWBFile.units table
            cluster_name = f'd{day} t{tet_num} c{cluster_num}'
            nwbf.add_unit(spike_times=spiketimes,
                          electrodes=tet_electrode_table_region[tet_num].data,
                          electrode_group=tet_electrode_group[tet_num],
                          obs_intervals=obs_int_each_epoch,
                          id=cluster_id,
                          cluster_name=cluster_name,
                          sorting_metric=-1,  # dummy value
                          )
            cluster_id += 1


def write_behavior(nwbf, data_dir, animal_prefix, day):
    # write position, head_direction, speed, linear position and apparatus
    # information

    position = pynwb.behavior.Position(name='Position')
    head_dir = pynwb.behavior.CompassDirection(name='Head Direction')
    speed = pynwb.behavior.BehavioralTimeSeries(name='Speed')
    linpos = pynwb.behavior.BehavioralTimeSeries(name='Linearized Position')

    behavior_data = ns.parse_franklab_behavior_data(
        data_dir, animal_prefix, day)
    epoch_time_ivls = []
    # column ordering of the behavioral data matrix
    time_idx, x_idx, y_idx, dir_idx, vel_idx = range(5)

    # load the linear position data
    try:
        linpos_data = ns.parse_franklab_linpos_data(
            data_dir, animal_prefix, day)
        linpos_found = True
    except FileNotFoundError:
        linpos_found = False

    # load the task information
    all_epochs_taskdata = ns.parse_franklab_task_data(
        data_dir, animal_prefix, day)

    # Initialize empty arrays for behavior samples across all epochs
    pos_samples = np.zeros((0, 2))  # x/y positions (n x 2)
    dir_samples = np.array([])
    speed_samples = np.array([])
    behavior_timestamps = []  # behavior timestamps are shared except linpos
    apparatus_dict = dict()
    statematrix_dict = dict()

    # Loop over each epoch of this day
    for epoch_num, epoch_data in behavior_data.items():
        m_per_pixel = epoch_data['cmperpixel'][0, 0] / \
            100  # meters / pixel conversion factor

        # Behavior samples for this epoch (position, head direction, speed)
        epoch_pos_samples = epoch_data['data'][:, (x_idx, y_idx)] * m_per_pixel
        epoch_dir_samples = epoch_data['data'][:, dir_idx]
        epoch_speed_samples = epoch_data['data'][:, vel_idx] * m_per_pixel

        # Timestamps for this epoch (note that we convert timestamps to
        # POSIX time)
        epoch_timestamps = (
            epoch_data['data'][:, time_idx] +
            nwbf.session_start_time.timestamp())

        # Add this epoch's data to the array
        pos_samples = np.concatenate((pos_samples, epoch_pos_samples), axis=0)
        dir_samples = np.concatenate((dir_samples, epoch_dir_samples), axis=0)
        speed_samples = np.concatenate(
            (speed_samples, epoch_speed_samples), axis=0)
        behavior_timestamps = np.concatenate(
            (behavior_timestamps, epoch_timestamps), axis=0)

        # Store the times of epoch start and end. We will use these later to
        # build the 'epochs' table
        epoch_time_ivls.append([epoch_timestamps[0], epoch_timestamps[-1]])

        # parse the task information structure
        task_data = all_epochs_taskdata[epoch_num]

        # skip any epochs without a defined type
        if 'type' not in task_data.keys():
            logger.info(
                f'Skipping {animal_prefix} day {day} epoch {epoch_num}:'
                ' no "type" field in task structure')
            continue

        if linpos_found and (task_data['type'][0] != 'sleep'):
            # for non-sleep box epochs we also need to process the linear
            # position from the statematrix element
            statematrix = linpos_data[epoch_num]['statematrix']
            # for each field in the statematrix we create a separate timeseries
            # object, and here we first concatenate the data. There is probably
            # a better way to do this.
            for key in list(statematrix.keys()):
                if key not in statematrix_dict:
                    statematrix_dict[key] = statematrix[key]
                else:
                    np.concatenate(
                        (statematrix_dict[key], statematrix[key]), axis=0)

    # adjust the statematrix timestamps
    if linpos_found:
        statematrix_dict['time'] = np.ndarray.flatten(
            np.asarray(statematrix_dict['time'] +
                       nwbf.session_start_time.timestamp()))

    # Add the across-epochs behavioral data to the PyNWB objects
    # See place_field_with_queries.ipynb for examples of how we query these for
    # specific epochs
    position.create_spatial_series(name='Position',
                                   timestamps=behavior_timestamps,
                                   data=pos_samples,
                                   reference_frame='corner of video frame')

    head_dir.create_spatial_series(
        name='Head direction',
        timestamps=behavior_timestamps,
        data=dir_samples,
        reference_frame=('0=direction of top of video frame; '
                         'positive values clockwise (need to confirm this)'))

    speed.create_timeseries(name='Speed',
                            timestamps=behavior_timestamps,
                            data=speed_samples,
                            unit='m/s',
                            description='smoothed movement speed estimate')

    # add timeseries to linpos
    for key in statematrix_dict.keys():
        if key == 'time':
            continue
        elif linpos_found:
            linpos.create_timeseries(
                name=key,
                timestamps=statematrix_dict['time'],
                data=statematrix_dict[key],
                unit='various',
                description='linear position statematrix information')

    # create a ProcessingModule for behavior data
    behav_mod = nwbf.create_processing_module(name='Behavior',
                                              description='Behavioral data')

    # Add the position, head direction and speed data to the ProcessingModule
    behav_mod.add_data_interface(position)
    behav_mod.add_data_interface(head_dir)
    behav_mod.add_data_interface(speed)
    if linpos_found:
        behav_mod.add_data_interface(linpos)

    # Now write apparatus and task data
    apparatus_dict = dict()
    for epoch_num in all_epochs_taskdata.keys():
        # parse the task information structure
        task_data = all_epochs_taskdata[epoch_num]
        if 'type' not in task_data.keys():
            continue
        # create the necessary apparati.
        # NOTE that in reality the same track has slightly different linear
        # coordinates in each epoch, but for simplicity we only take the one
        # from the first epoch for each track. As we are also saving the
        # linearized position this should be okay.
        if task_data['type'][0] == 'sleep':
            if 'Sleep Box' not in apparatus_dict.keys():
                # for sleep epochs we do not create an polygon, so we just
                # create an empty apparatus object
                apparatus_dict['Sleep Box'] = fle.Apparatus(
                    name='Sleep Box'.format(epoch_num), nodes=[], edges=[])
        else:
            apparatus_name = task_data['environment'][0]
            if apparatus_name not in apparatus_dict.keys():
                apparatus_dict[apparatus_name] = flh.get_apparatus_from_linpos(
                    linpos_data[epoch_num],
                    name=apparatus_name,
                    conversion=m_per_pixel)
    # create ProcessingModules for apparatus and task data
    apparatus_mod = nwbf.create_processing_module(name='Apparatus',
                                                  description='Apparatus data')
    task_mod = nwbf.create_processing_module(name='Task',
                                             description='Task data')
    for apparatus in apparatus_dict:
        apparatus_mod.add_data_interface(apparatus_dict[apparatus])

    task_name = 'Sleep'
    description = ('The animal_prefix sleeps or wanders freely around a small,'
                   ' empty box.')
    task_mod.add_data_interface(
        fle.Task(name=task_name, description=description))

    task_name = 'W-Alternation'
    task_description = ('The animal_prefix runs in an alternating W pattern'
                        ' between three neighboring arms of a maze.')
    task_mod.add_data_interface(
        fle.Task(name=task_name, description=task_description))

    # ---------
    # Add metadata columns to the NWBFile.epochs table
    # By default, it has columns for 'start_time', 'stop_time', and 'tags'.
    # ---------
    nwbf.add_epoch_column(
        name='exposure', description='number of exposures to this apparatus')
    nwbf.add_epoch_column(
        name='task', description='behavioral task for this epoch')
    nwbf.add_epoch_column(
        name='apparatus', description='behavioral apparatus for this epoch')

    # ---------
    # Iteratively add each epoch to the NWBFile.epochs table
    # ---------
    task_exposure_dict = dict()
    # the no exposure start num is used for sleep epochs, and the 1000*day
    # ensures that it's unique across days
    no_exposure_start_num = 1000 * day
    for epoch_num, epoch_metadata in all_epochs_taskdata.items():
        task_data = all_epochs_taskdata[epoch_num]
        if 'type' not in task_data.keys():
            continue

        # start and stop times were inferred from the behavior data earlier
        epoch_start_time, epoch_stop_time = epoch_time_ivls[epoch_num - 1]

        # meter per pixel ratio is also in the behavior data
        m_per_pixel = behavior_data[epoch_num]['cmperpixel'][0, 0] / 100

        # Frank Lab Task (from the "Task" ProcessingModule)
        epoch_task = flh.get_franklab_task(epoch_metadata, task_mod)

        # Frank Lab Apparatus (from the "Apparatus" ProcessingModule)
        epoch_apparatus = flh.get_franklab_apparatus(
            epoch_metadata, apparatus_mod)

        epoch_exposure_num = ns.get_exposure_num(epoch_metadata)
        # if this is -1 then we'll replace it with something that starts at 1e6
        # so it's always positive and incrementable in a sensible way
        if epoch_exposure_num == -1:
            # check to see if this is the first time that this task
            if epoch_task in task_exposure_dict.keys():
                task_exposure_dict[epoch_task] += 1
            else:
                task_exposure_dict[epoch_task] = no_exposure_start_num
        else:
            task_exposure_dict[epoch_task] = epoch_exposure_num

        # Required column 'tags'. We do not presently use this.
        epoch_tags = ''

        # Add this epoch to the NWBFile.epochs table
        # Note that task and apparatus are references to the "Behavior"
        # ProcessingModule, so they will not be unnecessarily duplicated within
        # the NWBFile
        nwbf.add_epoch(start_time=epoch_start_time,
                       stop_time=epoch_stop_time,
                       exposure=task_exposure_dict[epoch_task],
                       task=epoch_task,
                       apparatus=epoch_apparatus,
                       tags=epoch_tags)


def convert_to_nwb(data_dir, nwb_dir, animal_prefix, animal_name, days,
                   overwrite=False,
                   dataset_zero_time=datetime(
                       2006, 1, 1, 12, 0, 0, tzinfo=tz.gettz('US/Pacific')),
                   device='NSpike acquisition system',
                   experimenter='FrankLab Anonymous',
                   experiment_description=('Tetrode recordings from rat during'
                                           ' rest and task performance'),
                   session_description='data acquisition session'):
    '''Convert one or more days of data into NWB files.

    Parameters
    ----------
    data_dir : str
    nwb_dir : str
    animal_prefix : str
    days : list
    overwrite : bool, optional
    datatset_zero_time : datetime instance, optional
    device : str, optional
    experimenter : str, optional
    experiment_description : str, optional
    session_description : str, optional

    '''

    # check to see that the specified directories exist
    assert(os.path.isdir(data_dir)), "Error: Data directory does not exist."
    os.makedirs(nwb_dir, exist_ok=True)

    for day in days:
        # process the data for each day
        nwb_file_name = os.path.join(
            nwb_dir, f'{animal_prefix.lower()}_{day:02d}.nwb')

        logger.info(f'Converting {animal_name} day {day}')

        # open the file
        nwbf = pynwb.NWBFile(
            session_description=session_description,
            identifier=f'{animal_prefix}{day:04}',
            session_start_time=dataset_zero_time,
            file_create_date=datetime.now(tz.tzlocal()),
            lab='Frank Laboratory',
            experimenter=experimenter,
            institution='UCSF',
            experiment_description=experiment_description,
            session_id='{0}{1:04}'.format(animal_prefix, day))

        # write out the subject information
        # change when NWB date_of_birth bug fixed
        # nwbf.subject = pynwb.file.Subject(date_of_birth=unknown_birth_date,
        nwbf.subject = pynwb.file.Subject(description='Long Evans Rat',
                                          genotype='WT',
                                          sex='M',
                                          species='rat',
                                          subject_id=animal_name,
                                          weight='unknown')

        # Recording device
        # Represent our acquisition system with a 'Device' object
        recording_device = nwbf.create_device(name=device)

        # Electrodes and Electrode Groups
        write_ephys(nwbf, data_dir, animal_prefix, day, recording_device)

        # Behavioral data
        write_behavior(nwbf, data_dir, animal_prefix, day)

        with pynwb.NWBHDF5IO(nwb_file_name, mode='w') as iow:
            iow.write(nwbf)
        logger.info(f'Successfully wrote NWB file {nwb_file_name}\n')
