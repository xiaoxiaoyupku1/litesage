import os
import sys
import numpy as np
from numpy import zeros, complex128, float32, float64, frombuffer
from collections import OrderedDict
from typing import Union, List, Tuple, Dict
from struct import unpack
from binascii import b2a_hex
from logging import getLogger
from argparse import ArgumentParser
from pickle import dump
_logger = getLogger('.rawWaveReadLog')

def readFloat32(f):
    s = f.read(4)
    return unpack('f', s)[0]
def readFloat64(f):
    s = f.read(8)
    return unpack('d', s)[0]
def readComplex(f):
    s = f.read(16)
    (re, im) = unpack('dd', s)
    return complex(re, im)
def consume4Bytes(f):
    f.read(4)
def consume8Bytes(f):
    f.read(8)
def consume16Bytes(f):
    f.read(16)

class EncodingDetectError(Exception):
    """
    Exception raised when the encoding of a file cannot be detected
    """
    pass


def detect_encoding(file_path, expected_str='') -> str:
    """
    Simple strategy to detect file encoding.  If an expected_str is given the function will scan through the possible
    encodings and return a match.
    If an expected string is not given, it will use the second character is null, high chances are that this file has an
    'utf_16_le' encoding, otherwise it is assuming that it is 'utf-8'.
    :param file_path: path to the filename
    :type file_path: str
    :param expected_str: text which the file should start with
    :type expected_str: str
    :return: detected encoding
    :rtype: str
    """
    for encoding in ('utf-8', 'utf_16_le', 'cp1252', 'cp1250', 'shift_jis'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                f.seek(0)
        except UnicodeDecodeError:
            # This encoding didn't work, let's try again
            continue
        else:
            if len(lines) == 0:
                # Empty file
                continue
            if expected_str:
                if not lines[0].startswith(expected_str):
                    # File did not start with expected string
                    # Try again with a different encoding (This is unlikely to resolve the issue)
                    continue
            if encoding == 'utf-8' and lines[0][1] == '\x00':
                continue
            return encoding
    else:
        if expected_str:
            raise EncodingDetectError(f"Expected string \"{expected_str}\" not found in file:{file_path}")
        else:
            raise EncodingDetectError(f"Unable to detect encoding on log file: {file_path}")

class DataSet(object):
    """
    This is the base class for storing all traces of a RAW file. Returned by the get_trace() or by the get_axis()
    methods.
    Normally the user doesn't have to be aware of this class. It is only used internally to encapsulate the different
    implementations of the wave population.
    Data can be retrieved directly by using the [] operator.
    If numpy is available, the numpy vector can be retrieved by using the get_wave() method.
    The parameter whattype defines what is the trace representing in the simulation, Voltage, Current a Time or
    Frequency.
    """

    def __init__(self, name, whattype, datalen, numerical_type='real'):
        """Base Class for both Axis and Trace Classes.
        Defines the common operations between both."""
        self.name = name
        self.whattype = whattype
        self.numerical_type = numerical_type
        if numerical_type == 'double':
            self.data = zeros(datalen, dtype=float64)
        elif numerical_type == 'real':
            self.data = zeros(datalen, dtype=float32)
        elif numerical_type == 'complex':
            self.data = zeros(datalen, dtype=complex128)
        else:
            raise NotImplementedError

    def __str__(self):
        if isinstance(self.data[0], float):
            # data = ["%e" % value for value in self.data]
            return "name:'%s'\ntype:'%s'\nlen:%d\n%s" % (self.name, self.whattype, len(self.data), str(self.data))
        elif isinstance(self.data[0], complex):
            return "name: {}\ntype: {}\nlen: {:d}\n{}".format(self.name, self.whattype, len(self.data), str(self.data))
        else:
            data = [b2a_hex(value) for value in self.data]
            return "name:'%s'\ntype:'%s'\nlen:%d\n%s" % (self.name, self.whattype, len(self.data), str(data))

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def get_wave(self):
        """
        :return: Internal data array
        :rtype: numpy.array
        """
        return self.data


class Axis(DataSet):
    """This class is used to represent the horizontal axis like on a Transient or DC Sweep Simulation. It derives from
    the DataSet and defines additional methods that are specific for X axis.
    This class is constructed by the get_time_axis() method or by a get_trace(0) command. In RAW files the trace 0 is
    always the X Axis. Ex: time for .TRAN simulations and frequency for the .AC simulations.

    To access data inside this class, the get_wave() should be used, which implements the support for the STEPed data.
    IF Numpy is available, get_wave() will return a numpy array.

    In Transient Analysis and in DC transfer characteristic, LTSpice uses doubles to store the axis values.
    """

    def __init__(self, name: str, whattype: str, datalen: int, numerical_type: str = 'double'):
        super().__init__(name, whattype, datalen, numerical_type)
        self.step_info = None

    def _set_steps(self, step_info: List[dict]):
        self.step_info = step_info

        self.step_offsets = [None for _ in range(len(step_info))]

        # Now going to calculate the point offset for each step
        self.step_offsets[0] = 0
        i = 1
        k = 1
        while i < len(self.data):
            if self.data[i] == self.data[0]:
                # print(k, i, self.data[i], self.data[i+1])
                self.step_offsets[k] = i
                k += 1
            i += 1

        if k != len(self.step_info):
            raise SpiceReadException("The file a different number of steps than expected.\n" +
                                     "Expecting %d got %d" % (len(self.step_offsets), k))

    def step_offset(self, step: int):
        """
        In Stepped RAW files, several simulations runs are stored in the same RAW file. This function returns the
        offset within the binary stream where each step starts.

        :param step: Number of the step within the RAW file
        :type step: int
        :return: The offset within the RAW file
        :rtype: int
        """
        if self.step_info is None:
            if step > 0:
                return len(self.data)
            else:
                return 0
        else:
            if step >= len(self.step_offsets):
                return len(self.data)
            else:
                return self.step_offsets[step]

    def get_wave(self, step: int = 0):
        """
        Returns a vector containing the wave values. If numpy is installed, data is returned as a numpy array.
        If not, the wave is returned as a list of floats.

        If stepped data is present in the array, the user should specify which step is to be returned. Failing to do so,
        will return all available steps concatenated together.

        :param step: Optional step in stepped data raw files.
        :type step: int
        :return: The trace values
        :rtype: numpy.array
        """
        if step == 0:
            wave = self.data[:self.step_offset(1)]
        else:
            wave = self.data[self.step_offset(step):self.step_offset(step + 1)]
        if self.name == 'time':  # This is a bug in LTSpice, where the time axis values are sometimes negative
            return np.abs(wave)
        else:
            return wave

    def get_time_axis(self, step: int = 0):
        """
        **Deprecated**. Use get_wave() instead.

        Returns the time axis raw data. Please note that the time axis may not have a constant time step. LTSpice will
        increase the time-step in simulation phases where there aren't value changes, and decrease time step in
        the parts where more time accuracy is needed.

        :param step: Optional step number if reading a raw file with stepped data.
        :type step: int
        :return: time axis
        :rtype: numpy.array
        """
        assert self.name == 'time', \
            "This function is only applicable to transient analysis, where a bug exists on the time signal"
        return self.get_wave(step)

    def get_point(self, n, step: int = 0) -> Union[float, complex]:
        """
        Get a point from the dataset
        :param n: position on the vector
        :type n:int
        :param step: step index
        :type step: int
        :returns: Value of the data point
        :rtype: float or complex
        """
        return self.data[n + self.step_offset(step)]

    def __getitem__(self, item) -> Union[float, complex]:
        """This is only here for compatibility with previous code. """
        assert self.step_info is None, "Indexing should not be used with stepped data. Use get_point or get_wave"
        return self.data.__getitem__(item)

    def get_position(self, t, step: int = 0) -> Union[int, float]:
        """
        Returns the position of a point in the axis. If the point doesn't exist, an interpolation is done between the
        two closest points.
        For example, if the point requested is 1.0001ms and the closest points that exist in the axis are t[100]=1ms and
        t[101]=1.001ms, then the return value will be 100 + (1.0001ms-1ms)/(1.001ms-1ms) = 100.1

        :param t: point in axis to search for
        :type t: float
        :param step: step number
        :type step: int
        :returns: The position of parameter /t/ in the axis
        :rtype: int, float
        """
        if self.name == 'time':
            timex = self.get_time_axis(step)
        else:
            timex = self.get_wave(step)
        for i, x in enumerate(timex):
            if x == t:
                return i
            elif x > t:
                # Needs to interpolate the data
                if i == 0:
                    raise IndexError("Time position is lower than t0")
                frac = (t - timex[i-1])/(timex[i] - timex[i-1])
                return i - 1 + frac

    def get_len(self, step: int = 0) -> int:
        """
        Returns the length of the axis.
        :param step: Optional parameter the step index.
        :type step: int
        :return: The number of data points
        :rtype: int
        """
        return self.step_offset(step + 1) - self.step_offset(step)

    def __len__(self):
        if self.step_info is None:
            return len(self.data)
        else:
            return self.get_len()

    def __iter__(self):
        assert self.step_info is None, "Iteration can't be used with stepped data. Use get_wave() method."
        return self.data.__iter__()


class TraceRead(DataSet):
    """This class is used to represent a trace. It derives from DataSet and implements the additional methods to
    support STEPed simulations.
    This class is constructed by the get_trace() command.
    Data can be accessed through the [] and len() operators, or by the get_wave() method.
    If numpy is available the get_wave() method will return a numpy array.
    """

    def __init__(self, name, whattype, datalen, axis, numerical_type='real'):
        super().__init__(name, whattype, datalen, numerical_type)
        self.axis = axis

    def get_point(self, n: int, step: int = 0) -> Union[float, complex]:
        """
        Implementation of the [] operator.

        :param n: item in the array
        :type n: int
        :param step: Optional step number
        :type step: int
        :return: float value of the item
        :rtype: float
        """
        if self.axis is None:
            if n != 0:
                return self.data[n]
            else:
                return self.data[step]  # This is for the case of stepped operation point simulation.
        else:
            return self.data[self.axis.step_offset(step) + n]

    def __getitem__(self, item) -> Union[float, complex]:
        """This is only here for compatibility with previous code. """
        assert self.axis is None or self.axis.step_info is None, \
            "Indexing should not be used with stepped data. Use get_point() method"
        return self.data.__getitem__(item)

    def get_wave(self, step: int = 0) -> np.array:
        """
        Returns the data contained in this object. For stepped simulations an argument must be passed specifying the
        step number. If no steps exist, the argument must be left blank.
        To know whether stepped data exist, the user can use the get_raw_property('Flags') method.

        If numpy is available the get_wave() method will return a numpy array.

        :param step: To be used when stepped data exist on the RAW file.
        :type step: int
        :return: a List or numpy array (if installed) containing the data contained in this object.
        :rtype: numpy.array
        """
        # print('step size %d' % step)
        # print(self.data[self.axis.step_offset(step):self.axis.step_offset(step + 1)])
        if self.axis is None:
            return super().get_wave()
        else:
            if step == 0:
                return self.data[:self.axis.step_offset(1)]
            else:
                return self.data[self.axis.step_offset(step):self.axis.step_offset(step + 1)]

    def get_point_at(self, t, step: int = 0) -> Union[float, complex]:
        """
        Get a point from the trace at the point specified by the /t/ argument.
        If the point doesn't exist on the axis, the data is interpolated using a linear regression between the two
        adjacent points.
        :param t: point in the axis where to find the point.
        :type t: float, float32(numpy) or float64(numpy)
        :param step: step index
        :type step: int
        """
        pos = self.axis.get_position(t, step)
        if isinstance(pos, (float, float32, float64)):
            offset = self.axis.step_offset(step)
            i = int(pos)
            last_item = self.get_len(step) - 1
            if i < last_item:
                f = pos - i
                return self.data[offset + i] + f * (self.data[offset + i + 1] - self.data[offset + i])
            elif pos == last_item:  # This covers the case where a float is given containing the last position
                return self.data[offset + i]
            else:
                raise IndexError(f"The highest index is {last_item}. Received {pos}")
        else:
            return self.get_point(pos, step)

    def get_len(self, step: int = 0) -> int:
        """
        Returns the length of the axis.
        :param step: Optional parameter the step index.
        :type step: int
        :return: The number of data points
        :rtype: int
        """
        return self.axis.step_offset(step + 1)

    def __len__(self):
        """
        **Deprecated**
        This is only here for compatibility with previous code.
        """
        assert self.axis is None or self.axis.step_info is None, \
            "len() should not be used with stepped data. Use get_len() method passing the step index"
        return len(self.data)


class DummyTrace(object):
    """Dummy Trace for bypassing traces while reading"""

    def __init__(self, name, whattype):
        """Base Class for both Axis and Trace Classes.
        Defines the common operations between both."""
        self.name = name
        self.whattype = whattype


class SpiceReadException(Exception):
    """Custom class for exception handling"""
    ...


class WaveInfo(object):
    """ LTSpice RAW files """
    headerLines = (
        'Title',
        'Date',
        'Plotname',
        'Output',
        'Flags',
        'No. Variables',
        'No. Points',
        'Offset',
        'Command',
        'Variables',
        'Backannotation',
    )
    ACCEPTED_PLOTNAMES = (
        'AC Analysis',
        'DC transfer characteristic',
        'Operating Point',
        'Transient Analysis',
        'Transfer Function',
        'Noise Spectral Density',
        'Frequency Response Analysis',
    )

    def __init__(self, raw_filename: str, traces_to_read: Union[str, List[str], Tuple[str, ...], None] = '*', **kwargs):
        self.verbose = kwargs.get('verbose', True)
        raw_filename = os.path.abspath(raw_filename)
        if traces_to_read is not None:
            assert isinstance(traces_to_read, (str, list, tuple)), "traces_to_read must be a string, a list or None"

        raw_file_size = os.stat(raw_filename).st_size  # Get the file size in order to know the data size
        raw_file = open(raw_filename, "rb")

        ch = raw_file.read(6)
        if ch.decode(encoding='utf_8') == 'Title:':
            self.encoding = 'utf_8'
            sz_enc = 1
            line = 'Title:'
        elif ch.decode(encoding='utf_16_le') == 'Tit':
            self.encoding = 'utf_16_le'
            sz_enc = 2
            line = 'Tit'
        else:
            raise RuntimeError("Unrecognized encoding")
        if self.verbose:
            _logger.debug("Reading the file with encoding ", self.encoding)
        # Storing the filename as part of the dictionary
        self.raw_params = OrderedDict(Filename=raw_filename)  # Initializing the dict that contains all raw file info
        self.backannotations = []  # Storing backannotations
        header = []
        binary_start = 6
        while True:
            ch = raw_file.read(sz_enc).decode(encoding=self.encoding)
            binary_start += sz_enc
            if ch == '\n':
                if self.encoding == 'utf_8':  # must remove the \r
                    line = line.rstrip('\r')
                header.append(line)
                if line in ('Binary:', 'Values:'):
                    self.raw_type = line
                    break
                line = ""
            else:
                line += ch
        for line in header:
            k, _, v = line.partition(':')
            if k == 'Variables':
                break
            self.raw_params[k] = v.strip()
        self.nPoints = int(self.raw_params['No. Points'], 10)
        self.nVariables = int(self.raw_params['No. Variables'], 10)

        has_axis = self.raw_params['Plotname'] not in ('Operating Point', 'Transfer Function',)

        self._traces = []
        self.steps = None
        self.axis = None  # Creating the axis
        self.flags = self.raw_params['Flags'].split()
        if 'complex' in self.raw_params['Flags'] or self.raw_params['Plotname'] == 'AC Analysis':
            numerical_type = 'complex'
        else:
            numerical_type = 'real'
        i = header.index('Variables:')
        ivar = 0
        for line in header[i + 1:-1]:  # Parse the variable names
            idx, name, var_type = line.lstrip().split('\t')
            if has_axis and ivar == 0:  # If it has an axis, it should be always read
                if numerical_type == 'real':
                    axis_numerical_type = 'double'
                else:
                    axis_numerical_type = numerical_type
                self.axis = Axis(name, var_type, self.nPoints, axis_numerical_type)
                trace = self.axis
            elif (traces_to_read == "*") or (name in traces_to_read):
                if has_axis:  # Reads data
                    trace = TraceRead(name, var_type, self.nPoints, self.axis, numerical_type)
                else:
                    # If an Operation Point or Transfer Function, only one point per step
                    trace = TraceRead(name, var_type, self.nPoints, None, 'real')
            else:
                trace = DummyTrace(name, var_type)

            self._traces.append(trace)
            ivar += 1

        if traces_to_read is None or len(self._traces) == 0:
            # The read is stopped here if there is nothing to read.
            raw_file.close()
            return

        if kwargs.get("headeronly", False):
            raw_file.close()
            return

        if self.verbose:
            _logger.info("File contains {} traces, reading {}".format(ivar,
                                                               len([trace for trace in self._traces
                                                                    if not isinstance(trace, DummyTrace)])))

        if self.raw_type == "Binary:":
            # Will start the reading of binary values
            # But first check whether how data is stored.
            self.block_size = (raw_file_size - binary_start) // self.nPoints
            self.data_size = self.block_size // self.nVariables

            scan_functions = []
            for trace in self._traces:
                if self.data_size == 8:
                    if isinstance(trace, DummyTrace):
                        fun = consume8Bytes
                    else:
                        fun = readFloat64
                elif self.data_size == 16:
                    if isinstance(trace, DummyTrace):
                        fun = consume16Bytes
                    else:
                        fun = readComplex
                else:  # data size is only 4 bytes
                    if len(scan_functions) == 0:  # This is the axis
                        fun = readFloat64
                    else:
                        if isinstance(trace, DummyTrace):
                            fun = consume4Bytes
                        else:
                            fun = readFloat32
                scan_functions.append(fun)

            if "fastaccess" in self.raw_params["Flags"]:
                if self.verbose:
                    _logger.debug("Binary RAW file with Fast access")
                # Fast access means that the traces are grouped together.
                for i, var in enumerate(self._traces):
                    if isinstance(var, DummyTrace):
                        # TODO: replace this by a seek
                        raw_file.read(self.nPoints * self.data_size)
                    else:
                        if self.data_size == 8:
                            s = raw_file.read(self.nPoints * 8)
                            var.data = frombuffer(s, dtype=float64)
                        elif self.data_size == 16:
                            s = raw_file.read(self.nPoints * 16)
                            var.data = frombuffer(s, dtype=complex)
                        else:
                            if i == 0:
                                s = raw_file.read(self.nPoints * 8)
                                var.data = frombuffer(s, dtype=float64)
                            else:
                                s = raw_file.read(self.nPoints * 4)
                                var.data = frombuffer(s, dtype=float32)

            else:
                if self.verbose:
                    _logger.debug("Binary RAW file with Normal access")
                # This is the default save after a simulation where the traces are scattered
                for point in range(self.nPoints):
                    for i, var in enumerate(self._traces):
                        value = scan_functions[i](raw_file)
                        if value is not None and not isinstance(var, DummyTrace):
                            var.data[point] = value

        elif self.raw_type == "Values:":
            if self.verbose:
                _logger.debug("ASCII RAW File")
            # Will start the reading of ASCII Values
            for point in range(self.nPoints):
                first_var = True
                for var in self._traces:
                    line = raw_file.readline().decode(encoding=self.encoding, errors='ignore')
                    if first_var:
                        first_var = False
                        s_point = line.split("\t", 1)[0]

                        if point != int(s_point):
                            _logger.error("Error Reading File")
                            break
                        value = line[len(s_point):-1]
                    else:
                        value = line[:-1]
                    if not isinstance(var, DummyTrace):
                        var.data[point] = float(value)
        else:
            raw_file.close()
            raise SpiceReadException("Unsupported RAW File. ""%s""" % self.raw_type)

        raw_file.close()

        # Setting the properties in the proper format
        self.raw_params["No. Points"] = self.nPoints
        self.raw_params["No. Variables"] = self.nVariables
        self.raw_params["Variables"] = [var.name for var in self._traces]
        # Now Purging Dummy Traces
        i = 0
        while i < len(self._traces):
            if isinstance(self._traces[i], DummyTrace):
                del self._traces[i]
            else:
                i += 1

        # Finally, Check for Step Information
        if "stepped" in self.raw_params["Flags"]:
            try:
                self._load_step_information(raw_filename)
            except SpiceReadException:
                _logger.warning("LOG file for ""%s"" not found or problems happened while reading it.\n"
                                " Auto-detecting steps" % raw_filename)
                if has_axis:
                    number_of_steps = 0
                    for v in self.axis.data:
                        if v == self.axis.data[0]:
                            number_of_steps += 1
                else:
                    number_of_steps = self.nPoints
                self.steps = [{'run': i + 1} for i in range(number_of_steps)]

            if self.steps is not None:
                if has_axis:
                    # Individual access to the Trace Classes, this information is stored in the Axis
                    # which is always in position 0
                    self._traces[0]._set_steps(self.steps)

    def get_raw_property(self, property_name=None):
        """
        Get a property. By default, it returns all properties defined in the RAW file.

        :param property_name: name of the property to retrieve.
        :type property_name: str
        :returns: Property object
        :rtype: str
        :raises: ValueError if the property doesn't exist
        """
        if property_name is None:
            return self.raw_params
        elif property_name in self.raw_params.keys():
            return self.raw_params[property_name]
        else:
            raise ValueError("Invalid property. Use %s" % str(self.raw_params.keys()))

    def get_sim_type(self):
        """
        Get simulation type: dc, ac, tran
        TODO: to complete all simulation types
        DC transfer characteristic
        ...
        """
        return self.get_raw_property('Plotname').split()[0].lower()

    def get_trace_names(self):
        """
        Returns a list of exiting trace names of the RAW file.

        :return: trace names
        :rtype: list[str]
        """
        return [trace.name for trace in self._traces]

    def get_trace(self, trace_ref: Union[str, int]):
        """
        Retrieves the trace with the requested name (trace_ref).

        :param trace_ref: Name of the trace or the index of the trace
        :type trace_ref: str or int
        :return: An object containing the requested trace
        :rtype: DataSet subclass
        :raises IndexError: When a trace is not found
        """
        if isinstance(trace_ref, str):
            for trace in self._traces:
                if trace_ref.upper() == trace.name.upper():  # The trace names are case-insensitive
                    # assert isinstance(trace, DataSet)
                    return trace
            raise IndexError(f"{self} doesn't contain trace \"{trace_ref}\"\n"
                             f"Valid traces are {[trc.name for trc in self._traces]}")
        else:
            return self._traces[trace_ref]

    def get_wave(self, trace_ref: Union[str, int], step: int = 0):
        """
        Retrieves the trace data with the requested name (trace_ref), optionally providing the step number.

        :param trace_ref: Name of the trace or the index of the trace
        :type trace_ref: str or int
        :param step: Optional parameter specifying which step to retrieve.
        :type step: int
        :return: A numpy array containing the requested waveform.
        :rtype: numpy.array
        :raises IndexError: When a trace is not found
        """
        return self.get_trace(trace_ref).get_wave(step)

    def get_waves(self, step: int = 0):
        """
        Retrieves all trace data in order of trace names, optionally providing the step number
        """
        wave = None
        for trace_ref in self.get_trace_names():
            if wave is not None:
                wave = np.vstack((wave, self.get_wave(trace_ref)))
            else:
                wave = self.get_wave(trace_ref)
        return wave


    def get_time_axis(self, step: int = 0):
        """
        *(Deprecated)* Use get_axis method instead

        This function is equivalent to get_trace('time').get_time_axis(step) instruction.
        It's workaround on a LTSpice issue when using 2nd Order compression, where some values on
        the time trace have a negative value."""
        return self.get_trace('time').get_time_axis(step)

    def get_axis(self, step: int = 0):
        """
        This function is equivalent to get_trace(0).get_wave(step) instruction.
        It also implements a workaround on a LTSpice issue when using 2nd Order compression, where some values on
        the time trace have a negative value.
        :param step: Step number
        :type step: int
        :returns: Array with the X axis
        :rtype: list[float] or numpy.array
        """
        if self.axis:
            axis = self.get_trace(0)
            assert isinstance(axis, Axis), "This RAW file does not have an axis."
            return axis.get_wave(step)
        else:
            raise RuntimeError("This RAW file does not have an axis.")

    def get_len(self, step: int = 0) -> int:
        """
        Returns the length of the data at the give step index.
        :param step: Optional parameter the step index.
        :type step: int
        :return: The number of data points
        :rtype: int
        """
        return self.axis.get_len(step)

    def _load_step_information(self, filename):
        # Find the extension of the file
        if not filename.endswith(".raw"):
            raise SpiceReadException("Invalid Filename. The file should end with '.raw'")
        logfile = os.path.splitext(filename)[0] + ".log"
        try:
            encoding = detect_encoding(logfile, "Circuit:")
            log = open(logfile, 'r', errors='replace', encoding=encoding)
        except OSError:
            raise SpiceReadException("Step information needs the '.log' file generated by LTSpice")
        except UnicodeError:
            raise SpiceReadException("Unable to parse log file and obtain .STEP information. Check Unicode")

        for line in log:
            if line.startswith(".step"):
                step_dict = {}
                for tok in line[6:-1].split(' '):
                    key, value = tok.split('=')
                    try:
                        # Tries to convert to float for backward compatibility
                        value = float(value)
                    except ValueError:
                        pass
                        # Leave value as a string to accommodate cases like temperature steps.
                        # Temperature steps have the form '.step temp=25°C'
                    step_dict[key] = value
                if self.steps is None:
                    self.steps = [step_dict]
                else:
                    self.steps.append(step_dict)
        log.close()

    def __getitem__(self, item):
        """Helper function to access traces by using the [ ] operator."""
        return self.get_trace(item)

    def get_steps(self, **kwargs):
        """Returns the steps that correspond to the query set in the * * kwargs parameters.
        Example: ::

            raw_read.get_steps(V5=1.2, TEMP=25)

        This will return all steps in which the voltage source V5 was set to 1.2V and the TEMP parameter is 24 degrees.
        This feature is only possible if a .log file with the same name as the .raw file exists in the same directory.
        Note: the correspondence between step numbers and .STEP information is stored on the .log file.

        :key kwargs:
         key-value arguments in which the key correspond to a stepped parameter or source name, and the value is the
         stepped value.

        :return: The steps that match the query
        :rtype: list[int]
        """
        if self.steps is None:
            return [0]  # returns a single step
        else:
            if len(kwargs) > 0:
                ret_steps = []  # Initializing an empty array
                i = 0
                for step_dict in self.steps:
                    for key in kwargs:
                        ll = step_dict.get(key, None)
                        if ll is None:
                            break
                        elif kwargs[key] != ll:
                            break
                    else:
                        ret_steps.append(i)  # All the step parameters match
                    i += 1
                return ret_steps
            else:
                return range(len(self.steps))  # Returns all the steps

    def export(self, columns: list = None, step: Union[int, List[int]] = -1, **kwargs) -> Dict[str, list]:
        """
        Returns a native python class structure with the requested trace data and steps.
        It consists of an ordered dictionary where the columns are the keys and the values are lists with the data.

        This function is used by the export functions.

        :param step: Step number to retrieve. If not given, it will return all steps
        :type step: int
        :param columns: List of traces to use as columns. Default is all traces
        :type columns: list
        :param kwargs: Additional arguments to pass to the pandas.DataFrame constructor
        :type kwargs: \*\*dict
        :return: A pandas DataFrame
        :rtype: pandas.DataFrame
        """
        if columns is None:
            columns = self.get_trace_names()  # if no columns are given, use all traces
        else:
            if self.axis and self.axis.name not in columns:  # If axis is not in the list, add it
                columns.insert(0, self.axis.name)

        if isinstance(step, list):
            steps_to_read = step  # If a list of steps is given, use it
        elif step == -1:
            steps_to_read = self.get_steps(**kwargs)  # If no step is given, read all steps
        else:
            steps_to_read = [step]  # If a single step is given, pass it as a list

        step_columns = []
        if len(step_columns) > 1:
            for step_dict in self.steps[0]:
                for key in step_dict:
                    step_columns.append(key)
        data = OrderedDict()
        # Create the headers with the column names and empty lists
        for col in columns:
            data[col] = []
        for col in step_columns:
            data[col] = []
        # Read the data
        for step in steps_to_read:
            for col in columns:
                data[col] += list(self.get_wave(col, step))
            for col in step_columns:
                data[col] += [self.steps[step][col]] * len(data[columns[0]])
        return data

    # def to_csv(self, filename, columns: list = None, step: Union[int, List[int]] = -1,
    #            separator=',', **kwargs):
    #     """
    #     Saves the data to a CSV file.

    #     :param filename: Name of the file to save the data to
    #     :type filename: str
    #     :param columns: List of traces to use as columns. Default is all traces
    #     :type columns: list
    #     :param step: Step number to retrieve. If not given, it
    #     :type step: int
    #     :param separator: separator to use in the CSV file
    #     :type separator: str
    #     :param kwargs: Additional arguments to pass to the pandas.DataFrame.to_csv function
    #     :type kwargs: \*\*dict
    #     """
    #     try:
    #         import pandas as pd
    #     except ImportError:
    #         use_pandas = False
    #     else:
    #         use_pandas = True

    #     if use_pandas:
    #         df = self.to_dataframe(columns=columns, step=step)
    #         df.to_csv(filename, sep=separator, **kwargs)
    #     else:
    #         # Export to CSV using python built-in functions
    #         data = self.export(columns=columns, step=step)
    #         with open(filename, 'w') as f:
    #             f.write(separator.join(data.keys()) + '\n')
    #             for i in range(len(data[columns[0]])):
    #                 f.write(separator.join([str(data[col][i]) for col in data.keys()]) + '\n')

    # def to_excel(self, filename, columns: list = None, step: Union[int, List[int]] = -1,
    #              **kwargs):
    #     """
    #     Saves the data to an Excel file.
    #     :param filename: Name of the file to save the data to
    #     :type filename: str
    #     :param columns: List of traces to use as columns. Default is all traces
    #     :type columns: list
    #     :param step: Step number to retrieve. If not given, it
    #     :type step: int
    #     :param kwargs: Additional arguments to pass to the pandas.DataFrame.to_excel function
    #     :type kwargs: \*\*dict
    #     """
    #     try:
    #         import pandas as pd
    #     except ImportError:
    #         raise ImportError("The 'pandas' module is required to use this function.\n"
    #                           "Use 'pip install pandas' to install it.")
    #     df = self.to_dataframe(columns=columns, step=step)
    #     df.to_excel(filename, **kwargs)


def parseWave():
    parser = ArgumentParser()
    parser.add_argument('-input', type=str, default='')
    parser.add_argument('-output', type=str, default='')

    args = parser.parse_args()
    inputFile = args.input  # .raw: must exist
    outputFile = args.output  # .sig: must not exist

    if not os.path.isfile(inputFile):
        print('input file not exist: {}'.format(inputFile))
        sys.exit()
    elif not inputFile.endswith('.raw'):
        print('input file not .raw format: {}'.format(inputFile))
        sys.exit()
    elif os.path.isfile(outputFile):
        print('output file already exist: {}'.format(outputFile))
        sys.exit()
    elif os.path.isfile(outputFile):
        print('output file not .sig format: {}'.format(outputFile))
        sys.exit()

    wave = WaveInfo(inputFile)
    # with open(outputFile, 'wb') as fport:
    #     if getsizeof(wave) < 102400000:  # 100MB
    #         dump(wave, fport)
    #         with open(sigStatusFile, 'w') as f:
    #             f.write('finish dump all')
    #     else:
    #         sigNames = wave.get_trace_names()
    #         dump(sigNames, fport)
    #         with open(sigStatusFile, 'w') as f:
    #             f.write('finish dump names')
    with open(outputFile, 'wb') as fport:
        dump(wave, fport)
        print('finish wave parsing to {}'.format(outputFile))