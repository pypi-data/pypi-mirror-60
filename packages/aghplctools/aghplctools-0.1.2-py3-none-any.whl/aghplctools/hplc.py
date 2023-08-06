import warnings
import os
import time
import re
import csv
import pylab as pl
from hein_utilities.files import Watcher
from hein_utilities.misc import find_nearest, front_pad
from unithandler.base import UnitFloat

# try to find ChemStation folder (priority: 'hplcfolder' environment variable > default install location)
if os.getenv('hplcfolder') is None:  # if the environment variable is not set
    if os.path.isdir('C:\\Chem32') is True:  # try default location for ChemStation
        hplcfolder = 'C:\\Chem32'
    else:
        warnings.warn(f'The hplcfolder envrionment variable is not set on this computer '
                      f'and the default folder does not exist, functionality will be reduced.')
        hplcfolder = None
else:
    hplcfolder = os.getenv('hplcfolder')


def pull_hplc_area_from_txt(filename):
    """
    Pulls HPLC area data from the specified Agilent HPLC output file
    Returns the data tables for each wavelength in dictionary format.
    Each wavelength table is a dictionary with retention time: peak area format.

    :param str filename: path to file
    :return: dictionary
    dict[wavelength][retention time (float)][width/area/height]
    """

    signals = {}  # output dictionary

    with open(filename, 'r', encoding='utf-16') as openfile:
        lines = openfile.readlines()
        for linenum, line in enumerate(lines):
            stripped = line.strip('\n')  # strip
            if stripped.startswith('Signal '):
                if stripped.startswith('Signal :'):
                    continue
                if linenum + 3 <= len(lines) and lines[linenum + 3].startswith('  #') is False:
                    continue  # skip if not a data table
                splitline = stripped.split()  # split the line
                if splitline[2].startswith('DAD') is False:  # skip if not a diode array table
                    continue
                wavelength = float(splitline[4].split('=')[1].split(',')[0])  # retrieve wavelength
                signals[wavelength] = {}
                offset = 5
                while lines[linenum + offset].startswith('Totals') is False:
                    datasplit = lines[linenum + offset].split()
                    offset += 1
                    try:  # check that the first value is an integer (peak number)
                        int(datasplit[0])
                    except ValueError:
                        continue
                    try:
                        signals[wavelength][float(datasplit[1])] = {  # retention time
                            'width': float(datasplit[3]),  # peak width
                            'area': float(datasplit[4]),  # peak area
                            'height': float(datasplit[5]),  # peak area
                        }
                    except ValueError:  # if there is an extra value in the Type column, values will be offset
                        # todo verify that this catch fits all cases
                        signals[wavelength][float(datasplit[1])] = {  # retention time
                            'width': float(datasplit[4]),  # peak width
                            'area': float(datasplit[5]),  # peak area
                            'height': float(datasplit[6]),  # peak area
                        }
    return signals


def pull_hplc_area(filename):
    """
    Legacy name for pull_hplc_area_from_txt

    :return: dictionary
    dict[wavelength][retention time (float)][width/area/height]
    """
    warnings.warn('This method has been refactored to pull_hplc_area_from_txt', DeprecationWarning, stacklevel=2)
    return pull_hplc_area_from_txt(filename)


def pull_hplc_area_from_csv(folder, report_name='Report'):
    """
    Pulls HPLC area data from the specified Agilent HPLC CSV report files.
    Returns the data tables for each wavelength in dictionary format.
    Each wavelength table is a dictionary with retention time: peak area format.

    Due to the unconventional way Agilent structures its CSV files pulling the data is
    a bit awkward. In essence, the report consists of one CSV files containing all the metadata,
    and further CSV files (one per detector signal) containing the data, but without
    column headers or other metadata. Thus, this function extracts bot data and
    metadata and stores them in the same format as the text based data parsing.

    :param folder: The folder to search for report files
    :param report_name: File name (without number or extension) of the report file

    :return: dictionary
    dict[wavelength][retention time (float)][width/area/height]
    """

    hplc_data = {}

    number_of_signals = 0
    signal_wavelengths = {}

    number_of_columns = 0
    column_headers = []
    column_units = []

    wavelength_pattern = re.compile('Sig=(\d+),')  # literal 'Sig=' followed by one or more digits followed by a comma

    metadata_file = os.path.join(folder, f'{report_name}00.CSV')

    # extract the metadata
    with open(metadata_file, newline='', encoding='utf-16') as f:
        # read CSV file into a list so we can iterate over it multiple times
        report = list(csv.reader(f))

        # find the number of signals
        for line in report:
            if line[0] == 'Number of Signals':
                number_of_signals = int(line[1])
                break

        # find the signal wavelengths and the associated signal number
        for signal_no in range(number_of_signals):
            for line in report:
                if line[0] == f'Signal {signal_no + 1}':
                    # use the RegEx capture group to conveniently extract the wavelength
                    wavelength = float(re.search(wavelength_pattern, line[1]).group(1))
                    signal_wavelengths[wavelength] = signal_no + 1

        # find the number of columns in the data files
        for line in report:
            if line[0] == 'Number of Columns':
                number_of_columns = int(line[1])
                break

        # find the column headers and units, currently unused, for future reference
        for header in range(number_of_columns):
            for line in report:
                if line[0] == f'Column {header + 1}':
                    column_headers.append(line[1].strip())
                    column_units.append(line[2].strip())

    # now iterate over the individual data files and extract the data
    for wavelength, signal_no in signal_wavelengths.items():
        hplc_data[wavelength] = {}

        # the data files are numbered, hopefully corresponding to the signal numbers
        data_file = os.path.join(folder, f'{report_name}0{signal_no}.CSV')

        with open(data_file, newline='', encoding='utf-16') as f:
            # this time the iterator is fine since we only need to go through once
            report = csv.reader(f)

            # munch through the lines and get the relevant data
            for line in report:
                retention_time = float(line[1])
                peak_width = float(line[3])
                peak_area = float(line[4])
                peak_height = float(line[5])

                hplc_data[wavelength][retention_time] = {
                    'width': peak_width,
                    'area': peak_area,
                    'height': peak_height
                }

    return hplc_data


def pull_metadata_from_csv(folder, report_name='Report'):
    """
    Pulls run metadata from the specified Agilent HPLC CSV report files.
    Returns the metadata describing the sample in dictionary format.

    :param folder: The folder to search for report files
    :param report_name: File name (without number or extension) of the report file

    :return: dictionary containing the metadata
    """

    metadata = {}

    metadata_file = os.path.join(folder, f'{report_name}00.CSV')

    # extract the metadata
    with open(metadata_file, newline='', encoding='utf-16') as f:
        # read CSV file into a list so we can iterate over it multiple times
        report = list(csv.reader(f))

        # find the number of signals
        for line in report:
            metadata[line[0]] = line[1]

    return metadata


def find_max_area(signals):
    """
    Returns the wavelength and retention time corresponding to the maximum area in a set of HPLC peak data.

    :param dict signals: dict[wavelength][retention time (float)][width/area/height]
    :return:
    """
    """
    example of signals: {wavelength {retention time { 'width': ,'area': ,'height':}}}
                        {
                        210.0: {0.435: {'width': 0.0599, 'area': 2820.54077, 'height': 750.42493}}, 
                        230.0: {0.435: {'width': 0.0576, 'area': 585.83862, 'height': 162.34517}}, 
                        254.0: {0.436: {'width': 0.0488, 'area': 24.25661, 'height': 6.77451}}
                        }
    """
    max_area = 0
    max_wavelength = None
    max_retention = None
    for wavelength in signals:
        for retention in signals[wavelength]:
            if signals[wavelength][retention]['area'] > max_area:
                max_area = signals[wavelength][retention]['area']
                max_wavelength = wavelength
                max_retention = retention

    return max_wavelength, max_retention, max_area


def pull_hplc_data_from_folder(folder, targets, wiggle=0.01, watchfor='Report.TXT'):
    """
    Pulls the HPLC integrations for all report files within the specified directory.
    This function was designed to pull all data from a given day. This method only pulls data which exists in the reports,
    which can result in asymmetric data for timepoint analysis (i.e. it assumes that subsequent runs are unrelated to
     others). If the data in a folder are for time-course analysis, use
     :py:currentmodule:`~aghplctools.hplc.pull_hplc_data_from_folder_timepoint`.


    :param folder: The folder to search for report files
    :param targets: target dictionary of the form {'name': [wavelength, retention time], ...}

    :param wiggle: the wiggle time around retention times
    :param watchfor: the name of the report file to watch
    :return: dictionary of HPLCTarget instances in the format {'name': HPLCTarget, ...}
    :rtype: dict
    """
    # todo fix to have similar functionality to v but not zero-pad
    raise NotImplementedError('This method has some fundamental flaws which need to be addressed. Please use '
                              'pull_hplc_data_from_folder_timepoint instead. ')
    targets = {  # store the targets in a vial attribute
        name: HPLCTarget(
            targets[name][0],  # wavelength
            targets[name][1],  # retention time
            name,
            wiggle=wiggle,
        ) for name in targets
    }

    files = Watcher(  # find all matching instances of the target file name
        folder,
        watchfor
    )

    for file in files:  # walk through specified path
        areas = pull_hplc_area_from_txt(file)  # pull the HPLC area
        for target in targets:  # update each target
            targets[target].add_from_pulled(areas)

    return files.contents, targets


def pull_hplc_data_from_folder_timepoint(folder, wiggle=0.02, watchfor='Report.TXT'):
    """
    Pulls all HPLC data from a folder assuming that the contents of a folder are from an ordered, time-course run (i.e.
    the contents of one report are related to the others in the folder). The method will automatically watch for new
    retention times and will prepopulate appearing values with zeros. The resulting targets will have a consistent
    number of values across the folder.

    :param folder: The folder to search for report files
    :param wiggle: the wiggle time around retention times
    :param watchfor: the name of the report file to watch
    :return: dictionary of HPLCTarget instances in the format {wavelength: {retention_time: HPLCTarget, ...}, ...}
    :rtype: dict
    """

    files = Watcher(  # find all matching instances of the target file name
        folder,
        watchfor,
    )

    targets = {}  # target storage dictionary
    filenames = []
    for file in files:  # walk across all matches
        areas = pull_hplc_area_from_txt(file)  # pull the HPLC area from file
        for wavelength in areas:  # for each wavelength
            selwl = find_nearest(  # find the appropriate wavelength in the dictionary
                targets,
                wavelength,
                1.,
            )
            if selwl is None:  # if the wavelength is not in the dictionary, create a key
                selwl = wavelength
                targets[selwl] = {}

            # currently defined targets
            current = [targets[selwl][target].retention_time for target in targets[selwl]]
            for ret in areas[selwl]:  # for each retention time in the wavelength
                selret = find_nearest(  # check for presence of retention time in targets
                    current,
                    ret,
                    wiggle,
                )
                if selret is None:  # if the retention time is not present in the targets, create target
                    targets[selwl][ret] = HPLCTarget(
                        wavelength,
                        ret,
                        wiggle=wiggle,
                    )

            for target in targets[selwl]:  # update each target
                targets[selwl][target].add_from_pulled(areas)

    total = len(filenames)  # total number of files
    for wavelength in targets:  # for each wavelength
        for target in targets[wavelength]:  # and each target
            # if the length of the pulled areas is less than the total number of files, front pad lists with 0.'s
            if len(targets[wavelength][target].areas) < total:
                targets[wavelength][target].areas = front_pad(targets[wavelength][target].areas, total)
                targets[wavelength][target].widths = front_pad(targets[wavelength][target].widths, total)
                targets[wavelength][target].heights = front_pad(targets[wavelength][target].heights, total)

    return files.contents, targets


class HPLCTarget(object):
    def __init__(self, wavelength, retention_time, name=None, wiggle=0.2):
        """
        A data storage class for tracking an HPLC retention target.

        :param float wavelength: wavelength to track the target on
        :param float retention_time: retention time to look for the target
        :param str name: convenience name
        :param float wiggle: wiggle value in minutes for finding the target around the retention_time (the window will
            be [retention_time-wiggle, retention_time+wiggle])
        """
        # todo track multiple wavelengths for a single target
        # todo create an overall manager to facilitate retrieval of target groups (e.g. grouped by wavelength)
        self.name = name
        self.wavelength = UnitFloat(wavelength, 'm', 'n', 'n')
        self.retention_time = UnitFloat(retention_time, 'min')  # todo figure out how to prevent m prefix for time
        self.wiggle = UnitFloat(wiggle, 'min')
        self.times = []  # tracks timepoints (e.g. reaction times)
        self.areas = []  # tracks peak areas
        self.widths = []  # tracks peak widths
        self.heights = []  # tracks peak heights

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.wavelength}, {self.retention_time})'

    def __getitem__(self, item):
        return self.retrieve_index(item)

    def add_value(self, area, width=0., height=0., timepoint=None):
        """
        Adds a value to the tracker lists.

        :param float area: area to add (required)
        :param float width: width to add (optional)
        :param float height: height to add (optional)
        :param float timepoint: timepoint to use (if None, the current time will be called)
        """
        if timepoint is None:  # create timepoint if None
            timepoint = time.time()
        self.times.append(timepoint)  # append timepoint
        self.areas.append(area)  # append area
        # store width and height
        self.widths.append(width)
        self.heights.append(height)

    def add_from_pulled(self, signals, timepoint=None):
        """
        Retrieves values from the output of the pull_hplc_area function and stores them in the instance.

        :param dict signals: output dictionary from pull_hplc_area
        :param float timepoint: timepoint to save (if None, the current time will be retrieved)
        :return: area, height, width, timepoint
        :rtype: tuple
        """
        # initial values for area, height, and width
        area = 0.
        height = 0.
        width = 0.
        selwl = find_nearest(  # look for the tracked wavelength in the signals
            signals,
            self.wavelength,
            1.
        )
        if selwl is not None:  # if the target wavelength
            selret = find_nearest(  # look for the retention time
                signals[selwl],
                self.retention_time,
                self.wiggle,
            )
            if selret is not None:  # if retention time is present, retrieve values
                area = signals[selwl][selret]['area']
                height = signals[selwl][selret]['height']
                width = signals[selwl][selret]['width']
        self.add_value(  # store retrieved values
            area,
            width,
            height,
            timepoint,
        )
        return area, height, width, timepoint

    def retrieve_index(self, index):
        """
        Retrieves the values of the provided index.

        :param index: pythonic list index
        :return: {area, width, height, timepoint}
        :rtype: dict
        """
        try:
            return {
                'area': self.areas[index],
                'width': self.widths[index],
                'height': self.heights[index],
                'timepoint': self.times[index],
            }
        except IndexError:
            raise IndexError(f'The index {index} is beyond the length of the {self.__repr__()} object'
                             f' ({len(self.times)}')

    def retrieve_timepoint(self, timepoint):
        """
        Retrieves the values of the provided timepoint.

        :param float timepoint: time point to retrieve
        :return: {area, width, height, timepoint}
        :rtype: dict
        """
        return self.retrieve_index(
            self.times.index(  # index the timepoint
                find_nearest(  # find the nearest timepoint to the specified value (avoid floating point errors)
                    self.times,
                    timepoint,
                    0.001,
                )
            )
        )


def acquiring_filename():
    """
    Retrieves the path name of the next Agilent HPLC acquisition (from acquiring.txt)

    :return: file being currently acquired
    :rtype: str
    """
    with open(acqwatch.contents[0], 'r', encoding='utf-16') as acquiring:
        try:
            datafile = acquiring.readline().split('|')[1].strip()  # current data file
        # datafile = acquiring.readline().split(':')[1].strip()  # current data file
        except IndexError:
        # if len(datafile) == 0:  # first acquisition has an extra line, subsequent ones dont
            datafile = acquiring.readline().split('|')[1].strip()
            # datafile = acquiring.readline().split(':')[1].strip()  # current data file
        path = acqwatch.find_subfolder()[0]  # active sequence directory
        if datafile.endswith('.D') is False:  # catch in case it didn't point to a data file
            raise ValueError(f'ACQUIRING.TXT did not point to a data file (retrieved: {datafile})')
        datawatch.path = (
            os.path.join(  # set the datawatch path
                path,
                datafile
            )
        )
        return datafile


def plot(yvalues, xvalues=None, xlabel='injection #', ylabel=None, hline=None):
    """
    plots one set of values
    :param yvalues:  list of y values
    :param xvalues: list of x values (optional)
    :param xlabel: label for x
    :param ylabel: label for y
    :param hline: plot a horizontal line at this value if specified
    :return:
    """
    pl.clf()
    pl.close()
    fig = pl.figure()
    ax = fig.add_subplot(111)
    if xvalues is not None:
        ax.plot(xvalues, yvalues)
    else:
        ax.plot(yvalues)
    if hline is not None:
        ax.axhline(hline, color='r')
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    pl.show()


def stackedplot(rets, xlabel='injection #'):
    """
    Creates a stacked plot for the dictionary generated by pull_hplc_data_from_folder
    :param rets: dictionary of retetion times
    :param xlabel: optional changing of x label
    """
    pl.clf()
    pl.close()

    times = list(rets.keys())  # retention times
    targets = rets[times[0]].keys()  # target keys

    fig, ax = pl.subplots(len(targets), 1)  # create subplot stack
    for ind, val in enumerate(targets):
        for time in times:  # plot each time
            ax[ind].plot(
                rets[time][val],
                label='%.3f min' % time,
            )

        if ind != len(targets) - 1:  # remove x values if not the last subplot
            ax[ind].set_xticklabels([])
        ax[ind].set_ylabel(val)

    if xlabel is not None:
        ax[ind].set_xlabel(xlabel)
    handles, labels = ax[ind].get_legend_handles_labels()  # retrieve legend values
    ax[ind].legend(handles, labels)  # show legend
    pl.show()  # show


if hplcfolder is not None:
    datawatch = Watcher(  # create watcher for HPLC output files
        hplcfolder,
        'Report.TXT'
    )
    acqwatch = Watcher(  # watcher for acquiring text file
        hplcfolder,
        'ACQUIRING.TXT'
    )
else:
    datawatch = None
    acqwatch = None

