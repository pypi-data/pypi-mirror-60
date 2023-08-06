import re
import os
import datetime
from typing import List, Union
import xml.etree.ElementTree
from unithandler.base import UnitFloat

# regex to match signal patterns
signal_re = re.compile(
    '(?P<name>.+), '
    'Sig=(?P<wavelength>\d+),(?P<width>\d*) '
    'Ref=(?P<ref>off|(?P<ref_wl>\d+),(?P<ref_width>\d+))'
)


class DADSignalInfo(object):
    # default unit for wavelength values
    DEFAULT_WAVELENGTH_UNIT = 'nm'

    def __init__(self,
                 wavelength: Union[float, UnitFloat],
                 bandwidth: Union[float, UnitFloat] = 1.,
                 reference: Union["DADSignalInfo", str] = None,
                 name: str = None
                 ):
        """
        Class describing a DAD signal and its parameters

        :param wavelength: wavelength for the signal
        :param bandwidth: band width for the wavelength (signal is centered on the wavelength with this width)
        :param reference: reference information for the signal
        """
        self._wavelength = None
        self._bandwidth = None
        # todo UnitFloat
        self.wavelength = wavelength
        self.bandwidth = bandwidth
        if type(reference) is str:
            reference = DADSignalInfo.create_from_string(reference)
        self.reference: DADSignalInfo = reference
        self.name = name

    @property
    def wavelength(self) -> UnitFloat:
        """Wavelength for the signal"""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: Union[UnitFloat, float]):
        if type(value) is float:
            value = UnitFloat(
                value,
                self.DEFAULT_WAVELENGTH_UNIT,
            )
        self._wavelength = value

    @property
    def bandwidth(self) -> UnitFloat:
        """bandwidth for the signal wavelength"""
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, value: Union[UnitFloat, float]):
        if value is None:
            value = UnitFloat(
                1.,
                self.DEFAULT_WAVELENGTH_UNIT,
            )
        elif type(value) is float:
            value = UnitFloat(
                value,
                self.DEFAULT_WAVELENGTH_UNIT,
            )
        self._bandwidth = value

    @bandwidth.deleter
    def bandwidth(self):
        self.bandwidth = 1.

    def __str__(self):
        return (
            f'{f"{self.name} " if self.name is not None else ""}'
            # todo adjust str representation to not double-specify unit
            f'{self.wavelength},{self.bandwidth}'
            f'{f" {self.reference}" if self.reference is not None else ""}'
        )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.wavelength.real},'
            f'{self.bandwidth.real},'
            f'{self.reference},'  # todo adjust return of reference 
            f'{self.name}'
            f')'
        )

    @property
    def agilent_specification_string(self) -> str:
        """the specification string describing this instance (can be passed to create_from_string to reinstantiate)"""
        return (
            f'{self.name} '
            f'{int(self.wavelength.real)},{int(self.bandwidth.real)}'
            f'{f" {self.reference.agilent_specification_string}" if self.reference is not None else ""}'
        )

    @classmethod
    def create_from_string(cls,
                           string: str,
                           name_override: str = None,
                           ) -> 'DADSignalInfo':
        """
        Creates a class instance from a standard Agilent signal description string (e.g. 'DAD1 A, Sig=210,4 Ref=360,100')

        :param string: signal description string
        :param name_override: override for name specification
        :return: DADSignal object
        """
        match = signal_re.match(string)
        if match is None:
            raise ValueError(f'The string "{string}" could not be interpreted as a DADSignal')
        if match.group('ref') != 'off':
            ref = DADSignalInfo(
                wavelength=float(match.group('ref_wl')),
                bandwidth=float(match.group('ref_width')),
                name='Ref'
            )
        else:
            ref = None
        if name_override is None:
            name_override = match.group('name')
        return cls(
            wavelength=float(match.group('wavelength')),
            bandwidth=float(match.group('width')),
            reference=ref,
            name=name_override,
        )


# prefix regex to deal with irritating prefixed tree names
prefix_re = re.compile('(?P<prefix>.+)ACAML')
# regex to extract timezone from Agilent date time string
agilent_dt_re = re.compile('(?P<dt>.+)[-+].+')


class SampleInfo(object):
    def __init__(self,
                 sample_name: str,
                 datetimestamp: Union[str, datetime.datetime],
                 method_name: str,
                 signals: List[DADSignalInfo],  # todo
                 ):
        """
        Data class for describing an HPLC sample.

        :param sample_name: name for the data file
        :param datetimestamp: date and time stamp for when the sample was run
        :param method_name: method name used to run the sample
        :param signals: list of signals associated with the run
        """
        self.sample_name = sample_name
        if type(datetimestamp) is str:
            datetimestamp = datetime.datetime.strptime(
                agilent_dt_re.match(datetimestamp).group('dt'),
                '%Y-%m-%dT%H:%M:%S.%f'
            )
        self.datetimestamp: datetime.datetime = datetimestamp
        self.method_name = method_name
        self.signals: List[DADSignalInfo] = signals

    def __str__(self):
        return (
            f'{self.sample_name} run on {self.datetimestamp} with {len(self.signals)} signals'
        )

    @property
    def date(self) -> str:
        """date which the sample was run on"""
        return str(self.datetimestamp.date())

    @property
    def timestamp(self) -> str:
        """Time of the day when the sample was run"""
        return str(self.datetimestamp.time())

    def as_dict(self) -> dict:
        """Returns the sample data as a dictionary"""
        return {
            'sample_name': self.sample_name,
            'datetimestamp': str(self.datetimestamp),
            'method_name': self.method_name,
            'signals': [str(signal) for signal in self.signals]
        }

    @classmethod
    def create_from_acaml(cls, acaml: Union[str, xml.etree.ElementTree.ElementTree]) -> "SampleInfo":
        """
        Creates sample structure from an acaml file. (use sequence.acam_ in the desired .D folder)

        :param acaml: path to acaml file or parsed element tree root
        :return: parsed Sample instance
        """
        if type(acaml) is str:  # assume target path if string
            acaml = xml.etree.ElementTree.parse(
                os.path.join(
                    acaml,
                    'sequence.acam_'
                )
            )
        root = acaml.getroot()
        prefix = prefix_re.match(root.tag).group('prefix')

        # extract creation date
        cd = [val for val in root.iter(f'{prefix}CreationDate')][0]
        dt = datetime.datetime.strptime(
            agilent_dt_re.match(cd.text).group('dt'),
            '%Y-%m-%dT%H:%M:%S.%f'
        )

        # extract method name
        method = [val for val in root.iter(f'{prefix}Method')][0]
        method_name = [val.text for val in method.iter(f'{prefix}Name')][0]

        # sample name
        injection = [val for val in root.iter(f'{prefix}Injections')][0]
        # todo find better way to search this (multiple Name values in Injections tree)
        sample_name = [val.text for val in injection.iter(f'{prefix}Name')][0]

        signals = []
        for signal in root.iter(f'{prefix}Signal'):
            descrip = signal.find(f'{prefix}Description')
            try:
                signals.append(DADSignalInfo.create_from_string(descrip.text))
            except ValueError:
                pass

        return cls(
            sample_name=sample_name,
            method_name=method_name,
            datetimestamp=dt,
            signals=signals,
        )

