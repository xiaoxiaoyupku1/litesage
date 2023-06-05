import os
import numpy as np
from pathlib import Path
import multiprocessing

from src.wavefile.utils import NamedVal
from src.wavefile.utils import calcTopDiff
from src.wavefile.utils import plotname_to_plotnamestr

def _checkWavePlot(file1, file2, plotname, top=1):
    file1_fullpath = os.path.abspath(file1)
    file2_fullpath = os.path.abspath(file2)
    if file1_fullpath == file2_fullpath:
        print("  ****warning**** cheking wave for the same file:")
        print("  file 1 {}".format(file1))
        print("  file 2 {}".format(file2))
        return "pass", [], []
    from src.wavefile.wavefile import get_wavefile_handler
    # write import here to avoid cyclic import
    wave1 = get_wavefile_handler(file1)
    wave1.parseWaveFile()
    wave2 = get_wavefile_handler(file2)
    wave2.parseWaveFile()
    matching, *arg = wave2.checkWavePlot(wave1, plotname, top)
    print("+", end="", flush=True)
    return matching, arg


class WavefileHandler():
    def __init__(self, wavefile, debug=0):
        self.plotdata_list = []
        self.plotnames = []
        self.wavefile = os.path.abspath(wavefile)
        self.sigfiles = {}  # sig file name
        self.sigfiles_exist = {}
        self.large_file = False
        if not os.path.isfile(wavefile):
            print("  ****error**** wavefile not exist {}".format(wavefile))
            return
        else:
            self.large_file = self.is_largefile(wavefile)

    def unify_signame(self, signal_name):
        signal_name = signal_name.lower().replace("^", ".")
        if "(" not in signal_name:
            signal_name = "v({})".format(signal_name)
        return signal_name


    ## open api for wavefile handling
    def getSigNames(self, plotname=None):
        if plotname is None:
            assert len(self.plotdata_list) == 1, "wavefile {} has {} plots: {}, please specify the plot name to get_data".format(
                    self.wavefile, len(self.plotnames), ",".join(self.plotnames))
            return self.plotdata_list[0]["signames"]
        else:
            assert plotname in self.plotnames, "plotname {} not in plotnames: {}".format(
                    plotname, ",".join(self.plotnames))
            for plotdata in self.plotdata_list:
                if plotname == plotdata["plotname"]:
                    return plotdata["signames"]
            assert 0, "plotname {} not in plotname_list: {}".format(
                    plotname, ",".join(self.plotnames))
        return


    def get_data(self, plotname=None):
        if plotname is None:
            assert len(self.plotdata_list) == 1, "wavefile {} has {} plots: {}, please specify the plot name to get_data".format(
                    self.wavefile, ",".join(self.plotnames))
            return self.plotdata_list[0]["sigdata"]
        else:
            for plotdata in self.plotdata_list:
                if plotname == plotdata["plotname"]:
                    return plotdata["sigdata"]
            assert 0, "plotname {} not in plotname_list: {}".format(
                    plotname, ",".join(self.plotnames))
        return None


    def get_plotnames(self):
        return self.plotnames


    def is_largefile(self, wavefile):
        file_size = Path(wavefile).stat().st_size
        if file_size > 1000000000:  # 1 G
        # if file_size > 10000:  # 1G
        # if file_size > 5000000:
            print(" ****warning**** wavefile {} size {} is large, file handling will be slow".format(wavefile, file_size))
            return True
        return False


    def __del__(self):
        if self.large_file:
            print("  ****warning**** sigfiles left under {}".format(
                self.wavefile, self.sigfiles_dir))
            print("  keep the sigfiles will speedup wavefile handling nexttime")
            print("  you can manually delete them to save disc space")
        # if self.large_file:
        #     debugPrint("remove sigfiled dir: {}".format(self.sigfiles_dir))
        #     shutil.rmtree(self.sigfiles_dir)


    def is_valid_signal(self, var_name, var_type):
        if var_type == "voltage" or var_type.lower() == "v":
            if var_name.startswith("v("):
                return True
        if var_type == "current" or var_type.lower() == "a":
            if var_name.startswith("i("):
                return True
            if var_name.startswith("id("):
                return True
            if var_name.startswith("ib("):
                return True
        if var_type == "res-sweep" and var_name == "res-sweep":
            return True

        return False


    def is_valid_x_axis(self, plotname, var_name, var_type):
        if plotname == "tr":
            if var_name == "time" and var_type in ["time", "s"]:
                return True
        elif plotname == "ac":
            if var_name == "frequency" and var_type == "frequency":
                return True
        elif plotname == "dc":
            if self.is_valid_signal(var_name, var_type):
                return True

        if var_name == "temp-sweep" and var_type == "temp-sweep":
            return True
        if var_name == "v(v-sweep)" and var_type == "voltage":
            return True
        return False


    def is_sigfile_valid(self, sigfile, wavefile_mtime):
        """
        how to check the sigfile is valid and no need to re-generate it?
        1. sigfile exist
        2. sigfile latest modify time > wavefile modify time
        3. sigfile is complete, e.g., it has No. Points in the 6 th line
            becasue in the generate sigfile flow we
            1. write the sigfile header line, but the No. Points line value is empty
            2. write data to sigfile
            3. update No. Points value
        """
        pnt_cnt = 0
        if not os.path.isfile(sigfile):
            return False, pnt_cnt
        sigfile_mtime = os.path.getmtime(sigfile)
        if sigfile_mtime <= wavefile_mtime:
            return False, pnt_cnt
        with open(sigfile) as f:
            for i in range(5):
                line = f.readline()
            line = f.readline()
            line = line.strip()
            if not line.startswith("No. Points: "):
                return False, pnt_cnt
            line = line[12:].strip()
            try:
                pnt_cnt = int(line)
            except:
                return False, pnt_cnt
        return True, pnt_cnt


    def generate_sigfiles(self, plotname=None):
        if not self.large_file:
            return
        if plotname is None:
            plotname = self.plotname
        if plotname != "tr":
            # only for tr wavefile has special large file handling
            return

        # generate ngspice format wavefile
        wavefile = self.wavefile
        dirname = os.path.dirname(wavefile)
        basename = os.path.basename(wavefile)

        sigfiles_dir = os.path.join(dirname, "{}__sigfiles".format(basename))
        if not os.path.exists(sigfiles_dir):
            os.mkdir(sigfiles_dir)
        self.sigfiles_dir = sigfiles_dir

        sigfiles_exist = True
        pnt_cnt = 0
        sigfiles = {}
        wavefile_mtime = os.path.getmtime(self.wavefile)
        for signame in self.signames:
            sigfile = os.path.join(sigfiles_dir, "{}__{}__{}".format(basename, plotname, signame))
            sigfiles[signame] = sigfile
            if sigfiles_exist is False:
                continue
            _valid, _pnt_cnt = self.is_sigfile_valid(sigfile, wavefile_mtime)
            if _valid is False:
                sigfiles_exist = False
            elif _pnt_cnt <= 0:
                sigfiles_exist = False
            elif pnt_cnt <= 0:
                pnt_cnt = _pnt_cnt
            elif _pnt_cnt != pnt_cnt:
                sigfiles_exist = False

        self.sigfiles[plotname] = sigfiles
        self.sigfiles_exist[plotname] = sigfiles_exist
        if sigfiles_exist is True:
            self.pnt_cnt = pnt_cnt
            print("  ****info**** reuse sigfiles under {} for speedup".format(sigfiles_dir))
            return
        print("  ****info**** gen sigfiles under {}".format(sigfiles_dir))

        for sigtype, signame in zip(self.sigtypes, self.signames):
            sigfile = sigfiles[signame]
            if signame == "time":
                sigtype = "time"
            elif signame.startswith("v("):
                sigtype = "voltage"
            elif signame.startswith("i("):
                sigtype = "current"
            else:
                assert 0, "not valid signame: {}".format(signame)
            msg = "Title: {}\n".format(self.title)
            msg += "Date: {}\n".format(self.datetime)
            msg += "Plotname: {}\n".format(plotname_to_plotnamestr(plotname))
            msg += "Flags: real\n"
            if signame == "time":  # TODO
                msg += "No. Variables: 1\n"
            else:
                msg += "No. Variables: 2\n"
            msg += "No. Points: {}\n".format(" " * 10)  # unknown pnt_cnt, so just write place holder of space char
            msg += "Variables:\n"
            msg += "    0   {}    {}\n".format("time", "time")  # TODO
            if signame != "time":
                msg += "    1   {}    {}\n".format(signame, sigtype)  # TODO
            msg += "Values:\n"
            with open(sigfile, "w") as f:
                f.write(msg)

        self.sigfiles[plotname] = sigfiles


    def get_sigfile(self, signame=None, plotname=None):
        if not self.large_file:
            print("  ****sigfile not exist for small wavefile: {}".format(self.wavefile))
            return None

        if plotname is None:
            plotname = self.plotname
        if plotname != "tr":
            return None

        sigfile = self.sigfiles[plotname][signame]
        if not os.path.isfile(sigfile):
            print("  ****warning**** sigfile {} not exist".format(sigfile))

        return sigfile


    def update_sigfiles_pntcnt(self, pnt_cnt):
        # re-write pnt_cnt to the sigfile header
        for signame in self.signames:
            sigfile = self.get_sigfile(signame)
            with open(sigfile, "r+") as f:
                f.seek(0, 0)
                pos = 0
                for i in range(5):
                    # first 5 lines are: title, date, plotname, flags, No variables,
                    line = f.readline()
                    pos += len(line)
                f.seek(pos)
                f.write("No. Points: {}".format(pnt_cnt))
            is_largefile = self.is_largefile(sigfile)
            assert is_largefile is False, "sigfile too large: {}".format(sigfile)



    def getSigVals(self, plotname, signame=None):
        for plotdata in self.plotdata_list:
            if plotname != plotdata["plotname"]:
                continue
            if signame is None:
                # return all data with ndarray ndim = 2
                if self.large_file and plotname == "tr":
                    assert plotdata["sigdata"] is None
                    assert 0, "  ****error**** large wavefile {}, cannot get all signal values, suggest to get signal value one by one".format(self.wavefile)
                else:
                    return plotdata["sigdata"]
            else:
                signames = plotdata["signames"]
                assert signame.lower() in signames, "signame {} not in list ".format(signame)
                sigidx = signames.index(signame)
                if self.large_file and plotname == "tr":
                    sigfile = self.get_sigfile(signame, plotname)
                    from src.wavefile.wavefile import get_wavefile_handler
                    sigfilehandler = get_wavefile_handler(sigfile)
                    sigfilehandler.parseWaveFile()
                    assert sigfilehandler.large_file is False
                    sigval = sigfilehandler.getSigVals(plotname, signame)
                    return sigval
                else:
                    return plotdata["sigdata"][sigidx, :]

        print("  **warning** unrecognized plot name {}".format(plotname))
        return None


    def write_data_to_sigfiles(self, data, pnt_idx):
        assert len(data) == self.var_cnt
        # write x sigfile
        buf_pnt_cnt = len(data[0])
        sigfile = self.get_sigfile(self.signames[0])
        with open(sigfile, "a+") as f:
            for buf_pnt_idx in range(buf_pnt_cnt):
                f.write("{} {:.12e}\n".format(pnt_idx + buf_pnt_idx, data[0][buf_pnt_idx]))

        # write y sigfiles
        for sigidx in range(1, self.var_cnt):
            signame = self.signames[sigidx]
            sigfile = self.get_sigfile(signame)
            with open(sigfile, "a+") as f:
                for buf_pnt_idx in range(buf_pnt_cnt):
                    f.write("{} {:.12e}\n".format(pnt_idx + buf_pnt_idx, data[0][buf_pnt_idx]))
                    f.write("{:.12e}\n".format(data[sigidx][buf_pnt_idx]))


    def checkWave(self, other, top):
        """
        check the data with other wavefile handler object
        return matching (bool) and msg(str)
            matching = fail:
                plot / signal not match, msg will dump more information
            matching = pass:
                2 wavefile exactly matched
            matching = diff:
                2 wavefile have some value difference, msg will dump more information
        """
        matching = "pass"
        msg = ""
        if self.wavefile == other.wavefile:
            print("  ****warning**** files {} {} are the same file".format(self.wavefile, other.wavefile))
            return matching, msg

        missing_plotname0 = ""
        plotnames0_with_data = [plotdata["plotname"] for plotdata in other.plotdata_list]
        if other.plotnames != plotnames0_with_data:
            for missing_plotname0 in other.plotnames:
                if missing_plotname0 not in plotnames0_with_data:
                    break
            print("  ****warning**** {} has incomplete plot data: {}".format(other.wavefile, missing_plotname0))
            msg += "ref:  missing plot data: {}\n".format(missing_plotname0)
            matching = "fail"

        missing_plotname1 = ""
        plotnames1_with_data = [plotdata["plotname"] for plotdata in self.plotdata_list]
        if self.plotnames != plotnames1_with_data:
            for missing_plotname1 in self.plotnames:
                if missing_plotname1 not in plotnames1_with_data:
                    break
            print("  ****warning**** {} has incomplete plot data: {}".format(self.wavefile, missing_plotname1))
            msg += "this:  missing plot data: {}\n".format(missing_plotname1)
            matching = "fail"

        if matching == "fail" and missing_plotname1 != missing_plotname0:
            return matching, msg
        else:
            matching = "pass"

        if len(other.plotnames) == 0 or len(self.plotnames) == 0:
            msg = "missing plots\n"
            msg += "  ref: {}\n".format(",".join([plotdata["plotname"] for plotdata in other.plotdata_list]))
            msg += "  this: {}\n".format(",".join([plotdata["plotname"] for plotdata in self.plotdata_list]))
            matching = "fail"
            return matching, msg

        plotnames = []
        # will continue for plot not exactly match,
        # like for ngspice, we have op, dc , tr in one file
        # in hspice, op, dc, tr are in idfferent files, we will continue check the common data
        for plotname in plotnames0_with_data:
            if plotname in plotnames1_with_data:
                plotnames.append(plotname)

        if other.plotnames != self.plotnames:
            msg =  "  plot name not match: \n"
            msg += "    ref: {}\n".format(",".join([plotdata["plotname"] for plotdata in other.plotdata_list]))
            msg += "    this: {}\n".format(",".join([plotdata["plotname"] for plotdata in self.plotdata_list]))
            if len(plotnames) > 0:
                msg += "check for {}: \n".format(",".join(plotnames))
                matching = "fail"
            else:
                matching = "fail"
                return matching, msg

        # assert len(plotnames) == len(self.plotdata_list)
        # assert len(plotnames) == len(other.plotdata_list)
        for plotname in plotnames:
            _matching, *args = self.checkWavePlot(other, plotname, top)

            if _matching == "pass":
                pass
            elif _matching == "fail":
                matching = _matching
                _msg = args[0]
                msg += _msg
                return matching, msg
            else:
                assert _matching == "diff"
                matching = _matching
                topabsdiffs, topreldiffs = args
                msg += "  {}: \n".format(plotname)
                msg += "    top {} abs diff: ".format(top)
                for absdiff in topabsdiffs[:top]:
                    msg += "{} {:.4e}  ".format(absdiff._name, absdiff._value)
                msg += "\n"

                msg += "    top {} rel diff: ".format(top)
                for reldiff in topreldiffs[:top]:
                    msg += "{} {:.4e}%  ".format(reldiff._name, reldiff._value * 100)
                msg += "\n"

        return matching, msg


    def checkWavePlot(self, other, plotname, top):
        """ checkwave for plotname
        return: matching, *args
        if matching == 'pass' / 'fail', msg = args[0]
        if matching == 'diff':
            topabsdiffs, topreldiffs = arg[0], arg[1]
        """

        matching = "pass"
        msg = ""
        for plotdata0 in other.plotdata_list:
            if plotdata0["plotname"] == plotname:
                break
        for plotdata1 in self.plotdata_list:
            if plotdata1["plotname"] == plotname:
                break
        assert plotname == plotdata0["plotname"]
        assert plotname == plotdata1["plotname"]

        signames0 = plotdata0["signames"]
        signames1 = plotdata1["signames"]
        if signames0 != signames1:
            msg += "  {}: signame not match \n".format(plotname)
            msg += "    ref: {} signals: {} ...\n".format(len(signames0), ",".join(signames0[:5]))
            msg += "    this: {} signals: {} ...\n".format(len(signames1), ",".join(signames1[:5]))
            matching = "fail"
            if plotname == "op":
                pass
            elif plotname == "dc":
                # for dc, the sweep sinal name may have different names
                # like in psf, it may be volts, but in hsp, it is v-sweep
                pass
            elif signames0[0] != signames1[0]:
                return matching, msg

        signames = []  # common signames
        sigidxs0 = []  # common signames index in signames0
        sigidxs1 = []  # common signames index in signames1
        for sigidx0, signame in enumerate(signames0):
            if signame in signames1:
                signames.append(signame)
                sigidxs0.append(sigidx0)
                sigidxs1.append(signames1.index(signame))
        if len(signames) == 0:
            msg += "no same signames found\n"
            matching = "fail"
            return matching, msg

        if plotname == "tr" and (self.large_file or other.large_file):
            # large wavefile, no enough memory to handle all the signal data together
            # use a loop and compare one by one
            print("  **** info **** compare large wavefile signals one by one")
            absdiffs = []
            reldiffs = []

            # # use multi processing for speed up each sigfile checkwave
            cores = multiprocessing.cpu_count() - 4
            pool = multiprocessing.Pool(cores)

            arguments = []
            results = []
            for signame in signames[1:]:
                sigfile0 = other.wavefile
                if other.large_file:
                    sigfile0 = other.get_sigfile(signame, plotname)
                sigfile1 = self.wavefile
                if self.large_file:
                    sigfile1 = self.get_sigfile(signame, plotname)
                assert not self.is_largefile(sigfile0), "sigfile too large: {}".format(sigfile0)
                assert not self.is_largefile(sigfile1), "sigfile too large: {}".format(sigfile1)
                arguments.append([sigfile0, sigfile1, plotname, top])
            results = pool.starmap(_checkWavePlot, arguments)
            pool.close()

            for signame, result in zip(signames[1:], results):
                print("result for checkWavePlot signal {}".format(signame))
                matching, args = result
                print("matching is ", matching)

                if matching == "pass":
                    pass
                elif matching == "fail":
                    msg = args[0]
                    print("failed: {}".format(msg))
                elif matching == "diff":
                    _absdiffs, _reldiffs = args
                    absdiffs.extend(_absdiffs)
                    reldiffs.extend(_reldiffs)

            """
            for sigidx, signame in enumerate(signames):
                if sigidx == 0 and plotname == "tr":
                    continue
                print("  ****info**** checking for signal {} {}/{}".format(
                    signame, sigidx, len(signames)))
                sighandle0 = other
                sighandle1 = self
                if self.large_file:
                    sigfile1 = self.get_sigfile(signame, plotname)
                    sighandle1 = get_wavefile_handler(sigfile1)
                    assert sighandle1.large_file is False, \
                            "{} should be small wavefile".format(sighandle1.wavefile)
                    sighandle1.parseWaveFile()
                if other.large_file:
                    sigfile0 = other.get_sigfile(signame, plotname)
                    sighandle0 = get_wavefile_handler(sigfile0)
                    assert sighandle0.large_file is False, \
                            "{} should be small wavefile".format(sighandle0.wavefile)
                    sighandle0.parseWaveFile()
                _matching, *args = sighandle1.checkWavePlot(sighandle0, plotname, top)
                debugPrint("_matching = {}".format(_matching))
                debugPrint("args = {}".format(args))
                if _matching == "fail":
                    _msg = args[0]
                    matching = _matching
                    msg += _msg
                    print("  ****info**** matching is fail, msg:")
                    print(msg)
                    return matching, msg
                elif _matching == "pass":
                    print("  ****info**** matching is pass, no difference")
                    pass
                else:
                    assert _matching == "diff"
                    matching = _matching
                    _absdiffs, _reldiffs = args
                    absdiffs.extend(_absdiffs)
                    reldiffs.extend(_reldiffs)
                    assert len(_absdiffs) == len(_reldiffs)
                    if len(_absdiffs) == 0:
                        print("  ****info**** matching is pass, no difference")
                    else:
                        print("  abs diffs: {}, rel diffs: {}".format(_absdiffs[0]._value, _reldiffs[0]._value))
            """
            absdiffs.sort(reverse=True)
            reldiffs.sort(reverse=True)
            topabsdiffs = absdiffs[:top]
            topreldiffs = reldiffs[:top]

        else:
            array0 = plotdata0["sigdata"][sigidxs0, :]
            array1 = plotdata1["sigdata"][sigidxs1, :]

            matching, *args = self._compare_sigvals(plotname, signames, array0, array1, top)
            if matching == "pass" or matching == "fail":
                msg = args[0]
                return matching, msg
            elif matching == "diff":
                topabsdiffs, topreldiffs = args
        return matching, topabsdiffs, topreldiffs


    def _compare_sigvals(self, plotname, signames, array0, array1, top):
        # compare the signals value difference for array0 and array1
        sigcnt = len(signames)
        assert sigcnt == array0.shape[0], "sigcnt = {}, array0 shape = {}".format(sigcnt, array0.shape)
        assert sigcnt == array1.shape[0], "sigcnt = {}, array1 shape = {}".format(sigcnt, array1.shape)
        if top > sigcnt:
            top = sigcnt

        msg = ""
        if array0.shape == array1.shape and np.allclose(array0, array1, atol=1e-15):
            return "pass", ""

        assert array0.ndim == 2
        assert array1.ndim == 2
        assert len(signames) == array0.shape[0], "signames not match with data shape: {} {}".format(
                len(signames), array0.shape[0])
        assert len(signames) == array1.shape[0], "signames not match with data shape: {} {}".format(
                len(signames), array1.shape[0])

        if plotname == "op":
            # op has no x-axis
            topabsdiffs, topreldiffs = calcTopDiff(
                    array0, array1, signames, top)
        elif plotname in ["ac", "dc"]:
            # for ac and dc, the x-axis value should excatly match
            x0 = array0[0, :]
            x1 = array1[0, :]
            if x0.shape != x1.shape:
                msg += "{} x sweep data list size not match ".format(plotname)
                msg += "ref size: {}, this size: {}".format(str(x0.shape), str(x1.shape))
                matching = "fail"
                return matching, msg

            if not np.allclose(x0, x1, atol=1e-13):
                msg += "{} x sweep data list value not match ".format(plotname)
                matching = "fail"
                return matching, msg

            # ignore the x-axis sweep data
            topabsdiffs, topreldiffs = calcTopDiff(
                    array0[1:,:], array1[1:, :], signames[1:], top)

        elif plotname in ["tr"]:
            x0 = array0[0, :]
            x1 = array1[0, :]

            # check the tran time range matching or not
            if not np.allclose(x0[0], x1[0]):
                matching = "fail"
                msg += "  {} tran time range not match \n".format(plotname)
                return matching, msg
            if not np.allclose(x0[-1], x1[-1], atol=1e-15):
                matching = "fail"
                msg += "  {} tran time range not match \n".format(plotname)
                return matching, msg

            if array0.shape != array1.shape or not np.allclose(x0, x1, atol=1e-15):
                # use interpolation to generate the new data
                # as we only compare the max rel/abs difference,
                # no need to sort the signal values

                array0_interp = []  # use array0 value, array1 time for interpolation
                array1_interp = []  # use array1 value, array0 time for interpolation
                array0_interp.append(array0[:, 0].reshape(-1, 1))
                array1_interp.append(array1[:, 0].reshape(-1, 1))

                # interpolation:
                # index: ---------i1 ----------------------- i2
                #  time: ---------t1 ----- time ------------ t2
                # value: ---------v1 ----- v_interp--------- v2
                i1 = 0
                i2 = 0
                for time in x1[1:-1]:
                    while x0[i1 + 1] <= time:
                        i1 += 1
                    while x0[i2] <= time:
                        i2 += 1
                    assert x0[i1] <= time, "x0[i1] = {}, time = {}".format(x0[i1], time)
                    assert x0[i2] > time, "x0[i2] = {}, time = {}".format(x0[i2], time)
                    assert i1 + 1 == i2, "i1 = {}, i2 = {}".format(i1, i2)
                    t1 = x0[i1]
                    t2 = x0[i2]
                    v1 = array0[:, i1]
                    v2 = array0[:, i2]
                    v_interp = (v2 - v1) / (t2 - t1) * (time - t1) + v1
                    array0_interp.append(v_interp.reshape(-1, 1))
                array0_interp.append(array0[:, -1].reshape(-1, 1))
                array0_interp = np.concatenate(array0_interp, axis=1)
                assert array0_interp.shape == array1.shape, "x0 interp shape not match: {}, {}".format(
                        array0_interp.shape, array1.shape)

                i1 = 0
                i2 = 0
                for time in x0[1:-1]:
                    while x1[i1 + 1] <= time:
                        i1 += 1
                    while x1[i2] <= time:
                        i2 += 1
                    assert x1[i1] <= time
                    assert x1[i2] > time
                    assert i1 + 1 == i2, "i1 = {}, i2 = {}".format(i1, i2)

                    t1 = x1[i1]
                    t2 = x1[i2]
                    v1 = array1[:, i1]
                    v2 = array1[:, i2]
                    v_interp = (v2 - v1) / (t2 - t1) * (time - t1) + v1
                    array1_interp.append(v_interp.reshape(-1, 1))
                array1_interp.append(array1[:, -1].reshape(-1, 1))
                array1_interp = np.concatenate(array1_interp, axis=1)
                assert array1_interp.shape == array0.shape, "x1 interp shape not match: {}, {}".format(
                        array1_interp.shape, array0.shape)

                # merge 2 time list values, time points from x0 + time points from x1
                array0 = np.concatenate([array0, array0_interp], axis=1)
                array1 = np.concatenate([array1_interp, array1], axis=1)

            topabsdiffs, topreldiffs = calcTopDiff(
                    array0[1:], array1[1:], signames[1:], top)
        else:
            assert 0, "not valid plotname: {}".format(plotname)

        return "diff", topabsdiffs, topreldiffs
