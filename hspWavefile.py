import os
import struct
import numpy as np

from baseWavefile import WavefileHandler

class HspiceWavefileHandler(WavefileHandler):
    def __init__(self, wavefile, debug=0):
        super(HspiceWavefileHandler, self).__init__(wavefile, debug)
        self.sigtypes = []
        self.signames = []
        self.num_cnt_list = []

    def parseWavefile(self):
        fp = open(self.wavefile, 'rb')
        valid = self.parseWavefileHeader(fp)
        if not valid:
            print("  ****warning**** wavefile header not valid: {}".format(self.wavefile))
            return

        self.generate_sigfiles()
        self.parseWavefileData(fp)
        plotdata = {
                "plotname": self.plotname,
                "signames": self.signames,
                "sigdata": self.data,
                "mode": self.mode,
                "sigtypes": self.sigtypes,
                }
        self.plotdata_list.append(plotdata)

        fp.close()


    def _parseWavefileHeaderLine(self, header):
        header = header.strip()
        assert header.endswith("$&%#")
        header = header[:-4].strip()
        tokens = header.split()
        tokens.reverse()

        post_vers = header[0:24].strip()
        post_key  = post_vers[-4:]
        title     = header[24:88].strip()
        datetime  = header[88:264]
        tok       = datetime.split()
        datetime  = tok[0]
        colstring = header[264:]
        self.title = title
        self.datetime = datetime

        self.mc = False
        self.sweep = False
        if "0" in tokens:
            # no monte carlo, no sweep sweep
            # SWEEP?
            idx = tokens.index("0")
            tokens = tokens[:idx]
        elif "monte_carlo" in tokens:
            """
            monte carlo example 1:
            11
            3               1               1               1           1           1           1           1               1
            1               1               1               8           8           8           1
            k               v(0             v(gnda          v(in_neg    v(in_pos    v(out       v(vdda      v(xi82.net0148  v(xi82.net031
            v(xi82.net044   v(xi82.net058   v(xi82.net18    i(v2        i(v1        i(v0        v(in_pos,in_neg
            MONTE_CARLO     $&%#

            monte carlo example 2:
            30
            1               1               1               1               1               1               1
            1               1               1               1               1               1               1
            1               1
            8               8               1
            TIME            onoise          v(ibias_1       v(ibias_2       v(minus         v(out           v(plus
            v(vdd           v(0             v(xdut.sdb      v(xdut.vb1      v(xdut.vb2      v(xdut.vb3      v(xdut.vb4
            v(xdut.vb5      v(xdut.vb6
            i(vdd_dc        i(vplus_dc      inoise
            sweep           monte_carlo     $&%#
            """
            # for monte carlo cases, we now have a case in unittest
            # reverse loop to get the sinal count
            self.mc = True
            assert tokens[0] == "monte_carlo", "not valid tokens: {}".format(str(tokens))
            if tokens[1] == "sweep":
                tokens = tokens[2:]
                self.sweep = True
            else:
                tokens = tokens[1:]
            for tokidx, tok in enumerate(tokens):
                if tok.isdigit():
                    break
            tokens = tokens[: tokidx * 2]
        else:
            assert 0, "not valid format in wavefile header: {}".format(self.wavefile)
        sigtypes_signames = tokens
        sigtypes_signames.reverse()
        assert len(sigtypes_signames) % 2 == 0, "signame / sigtype in wavefile not match: {}".format(self.wavefile)
        sigcnt = int(len(sigtypes_signames) / 2)
        sigtypes, signames = sigtypes_signames[:sigcnt], sigtypes_signames[sigcnt:]
        for sigtype in sigtypes:
            assert sigtype.isdigit(), "not valid sigtype in wavefile: {} {}".format(sigtype, self.wavefile)
        sigtypes = [int(sigtype) for sigtype in sigtypes]
        signames = [signame.lower() for signame in signames]
        sighead_to_sigtype = {
                "time": 1,
                "v":    1,
                "hertz": 2,
                "vm":   2,
                "vp":   5,
                "vdb":  6,
                "vt":   7,
                "i":    8,
                "im":   9,
                "ip":   12,
                "idb":  13,
                "it":   14,
                "i1":   15,
                "ns": 51, "nr": 51, "nt": 51, "ni": 51, "nd": 51, "nf": 51, "ng": 51,
                "ncor": 51, "nigb":51, "nigd": 51, "nigs": 51, "nrbd": 51,
                "nrbpb": 51, "nrbpd": 51, "nrbps": 51, "nrbs": 51,
                "innoise": 51, "outnoise": 51,
                "inoise": 52, "onoise": 52,
                "par":  78,
                "lx":   79,
                "id":   91,
                "dt":   136,
                "isub": 152,
                "lstb": 188
                }
        self.num_cnt_list = []
        self.signames = []
        self.plotname = None
        for sigidx, signame in enumerate(signames):
            sigtype = sigtypes[sigidx]
            if sigidx == 0:
                if signame == "time":
                    self.plotname = "tr"
                    assert sigtype == 1
                elif signame == "hertz":
                    signame = "frequency"
                    self.plotname = "ac"
                    assert sigtype == 2
                elif signame == "deg_c":
                    signame = "temp-sweep"
                    self.plotname = "dc"
                elif signame == "volts":
                    self.plotname = "dc"
                    signame = "v(v-sweep)"
                else:
                    self.plotname = 'dc'
                self.num_cnt_list.append(1)
            else:
                if sigtype == 1:
                    # .probe name=v(n1)
                    if "(" not in signame:
                        signame = "v({})".format(signame)
                elif sigtype == 8:
                    # .probe name=i(v1)
                    if "(" not in signame:
                        signame = "i({})".format(signame)
                elif sigtype == 78:
                    if "(" not in signame:
                        signame = "par({})".format(signame)
                elif sigtype == 136:
                    assert "(" not in signame
                elif sigtype == 188:
                    if "(" not in signame:
                        signame = "lstb({})".format(signame)
                assert signame.startswith("i(") or \
                        signame.startswith("i1(") or \
                        signame.startswith("i2(") or \
                        signame.startswith("i3(") or \
                        signame.startswith("i4(") or \
                        signame.startswith("id(") or \
                        signame.startswith("idb(") or \
                        signame.startswith("im(") or \
                        signame.startswith("ip(") or \
                        signame.startswith("ir(") or \
                        signame.startswith("isub(") or \
                        signame.startswith("it(") or \
                        signame.startswith("v(") or \
                        signame.startswith("vdb(") or \
                        signame.startswith("vm(") or \
                        signame.startswith("vp(") or \
                        signame.startswith("vr(") or \
                        signame.startswith("vt(") or \
                        signame.startswith("lstb(") or \
                        signame.startswith("dt") or \
                        signame.startswith("par(") or \
                        signame.startswith("lx") or \
                        signame.startswith(("innoise", "outnoise")) or \
                        signame.startswith(("nr", "nt", "ni", "ns", "nd", "nf", "ng",
                                            "inoise", "onoise",
                                            "ncor", "nigb", "nigd", "nigs", "nrbd",
                                            "nrbpb", "nrbpd", "nrbps", "nrbs")), \
                        "not valid signal name in wavefile:{} {} ".format(self.wavefile, signame)
                if signame.startswith("lx"):
                    sighead = "lx"
                else:
                    sighead = signame.split("(")[0]
                if sigtype == 136:
                    sighead = sighead[:2]
                assert sigtype == sighead_to_sigtype[sighead], "sigtype {} is not {}".format(sigtype, sighead)
                if not signame.endswith(")") and "(" in signame:
                    signame += ")"
                if self.plotname == "ac":
                    if sighead.startswith(("hertz", "vp", "vm", "vdb", "vt", "lstb", "dt",
                                           "nr", "nt", "ni", "ns", "nd", "nf", "ng",
                                           "ncor", "nigb", "nigd", "nigs", "nrbd",
                                           "nrbpb", "nrbpd", "nrbps", "nrbs",
                                           "innoise", "outnoise", "inoise", "onoise")):
                        self.num_cnt_list.append(1)
                    elif sighead == 'par':
                        #and signame.split("(")[1].strip() in ["hertz", "vp", "vm", "vdb"]:
                        self.num_cnt_list.append(1)
                    elif sighead in ["v", "i"]:
                        self.num_cnt_list.append(2)
                    else:
                        assert 0, "not implemented signames for {}, wavefile {}".format(\
                                signame, self.wavefile)
                else:
                    self.num_cnt_list.append(1)
            self.signames.append(signame)
        self.num_cnt = sum(self.num_cnt_list)
        self.var_cnt = len(signames)
        self.pnt_cnt = None
        self.sigtypes = sigtypes
        self.plotnames.append(self.plotname)


class HspiceTxtWavefileHandler(HspiceWavefileHandler):
    def __init__(self, wavefile, debug=0):
        super(HspiceTxtWavefileHandler, self).__init__(wavefile, debug)
        self.mode = "txt"


    def parseWavefileHeader(self, fp):
        header = ""
        while True:
            c = struct.unpack('c', fp.read(1))[0].decode("utf-8")
            if c == '\n':
                continue
            header += c
            if header.endswith("$&%#"):
                break
        assert header.endswith("$&%#")
        self._parseWavefileHeaderLine(header)
        return True


    def parseWavefileData(self, fp):
        """
        txt format wavefile format example:

          000400000000000000002001** generated for: hspiced
          11/30/2020      14:55:16 Copyright (c) 1986 - 2020 by Synopsys, Inc. All
          Rights Reserved.          0
          3       1       1       8     DEG_C           v(0
          v(n1            i(v1            $&%#
          -.4000000E+020.0000000E+00-.5000000E+00-.5000000E+01-.3900000E+020.0000000E+00
          -.5000000E+00-.5000000E+01-.3800000E+020.0000000E+00-.5000000E+00-.5000000E+01
          -.3700000E+020.0000000E+00-.5000000E+00-.5000000E+01-.3600000E+020.0000000E+00
          ...

            remember: for ac0 file, each signal may have 13 or 2 of 13 chars, depends on the sigtypes
            check self.num_cnt_list
        """
        if self.large_file:
            assert 0, "not implemented for large file for hspice txt wavefile "

        sigvals = []
        digcnt = 13
        data = ""
        while True:
            line = fp.readline().decode("utf-8")
            if line == "":
                break
            line = line.replace(" ", "").replace("\n", "")
            data += line
            while len(data) >= digcnt:
                val, data = data[:digcnt], data[digcnt:]
                sigvals.append(float(val))
        assert data == "", "not valid wavefile format: {}".format(self.wavefile)
        assert sigvals[-1] == 0.1000000E+31, "data string not endswith '0.1000000E+31': {}".format(self.wavefile)
        sigvals = sigvals[:-1]
        assert len(sigvals) % self.num_cnt == 0, \
                "data string not matched, plotname = {}, sigvals size = {}, sigcnt = {}, numcnt = {}, wavefile = {}".format(
                        self.plotname, len(sigvals), self.var_cnt,  self.num_cnt, self.wavefile)
        self.pnt_cnt = int(len(sigvals) / self.num_cnt)

        assert self.num_cnt >= self.var_cnt
        if self.plotname != "ac":
            assert self.var_cnt == self.num_cnt, "var_cnt {} != num_cnt {}".format(self.var_cnt, self.num_cnt)
            self.data = np.array(sigvals).reshape(self.pnt_cnt, self.var_cnt).transpose()
        else:
            # for ac, some signal are complex and have 2 13 characters
            array = np.array(sigvals).reshape(self.pnt_cnt, self.num_cnt).transpose()
            self.data = np.empty((self.var_cnt, self.pnt_cnt), dtype=float)
            num_idx = 0
            for var_idx in range(self.var_cnt):
                if self.num_cnt_list[var_idx] == 1:
                    self.data[var_idx, :] = array[num_idx, :]
                else:
                    self.data[var_idx, :] = np.sqrt(array[num_idx, :] * array[num_idx, :] + array[num_idx +1, :] * array[num_idx +1, :])
                num_idx += self.num_cnt_list[var_idx]

            assert self.data.ndim == 2, "wrong array ndim: {}".format(str(self.data.ndim))
            assert self.data.shape[0] == self.var_cnt, "{} wrong array shape: {}, {}".format(
                    self.wavefile, str(self.data.shape), self.var_cnt)


class HspiceIc0WavefileHandler(HspiceWavefileHandler):
    def __init__(self, wavefile, debug=0):
        super(HspiceIc0WavefileHandler, self).__init__(wavefile, debug)
        self.mode = "ic0"
        self.nodeset_or_ic = ""


    def parseWavefileHeader(self, fp):
        fp.seek(0, 0)
        while True:
            line = fp.readline().decode("utf-8")
            if line == "":
                break
            line = line.strip()
            if line.startswith("*"):
                continue
            if line.startswith(".nodeset"):
                self.nodeset_or_ic = "nodeset"
                break
            if line.startswith(".ic"):
                self.nodeset_or_ic = "ic"
                break
            continue
        assert self.nodeset_or_ic in ["nodeset", "ic"], "expect .ic or .nodeset in file {}".format(self.wavefile)
        self.plotname = "op"
        self.plotnames.append(self.plotname)
        return True


    def parseWavefileData(self, fp):
        """
        + avs = 0.000e+00
        + b500mv = 4.951e-01
        + bias_p1 = 4.180e+00
        """
        self.signames = []
        data = []
        while True:
            line = fp.readline().decode("utf-8")
            if line == "":  # end of file
                break
            line = line.strip()
            if line.startswith("*"):
                continue
            assert line.startswith("+"), "{} not valid line: {}".format(self.wavefile, line)
            line = line[1:].strip()
            tokens = line.split()
            assert len(tokens) == 3, "{} not valid line: {}".format(self.wavefile, line)
            signame, equal, valstr = tokens
            assert "(" not in signame
            signame = "v({})".format(signame)
            self.signames.append(signame)

            if valstr.endswith("m"):
                val = float(valstr[:-1]) * 1.0e-3
            else:
                val = float(valstr)
            data.append(val)

        self.var_cnt = len(self.signames)
        self.pnt_cnt = 1
        self.data = np.asarray(data).reshape([self.var_cnt, self.pnt_cnt])


class HspiceBinWavefileHandler(HspiceWavefileHandler):
    def __init__(self, wavefile, debug=0):
        super(HspiceBinWavefileHandler, self).__init__(wavefile, debug)
        self.mode = "bin"


    def parseWavefileHeader(self, fp):
        # ------------------------------
        # limits: 4 (number of int32) 4 (number of bytes)
        # ------------------------------
        header = ""
        fp.seek(0, 0)
        while True:
            limits = np.frombuffer(fp.read(4*4), dtype="int32")
            _header = fp.read(limits[3]).decode("ascii")
            header += _header
            if _header.strip().endswith("$&%#"):
                break
            nprev = np.frombuffer(fp.read(4), dtype="int32")

        post_key = header[0:24].strip()[-4:]
        self._parseWavefileHeaderLine(header)

        if post_key == "9601":
            self.timesize, self.timepack, self.timetype = (4, "4B", "f")
            self.vsigsize, self.vsigpack, self.vsigtype = (4, "4B", "f")
        else :
            self.timesize, self.timepack, self.timetype = (8, "8B", "d")
            self.vsigsize, self.vsigpack, self.vsigtype = (4, "4B", "f")

        return True


    def _dump_data_to_sigfiles(self, bindata, pnt_data_size, pnt_cnt):
        """
        bindata: current dumping data buffer
        pnt_cnt: current pnt index in all the full file
        """
        if not self.large_file:
            return

        bin_pnt_cnt = int(len(bindata) / pnt_data_size)
        data = [[] for i in range(self.var_cnt)]
        for pnt_idx in range(bin_pnt_cnt):
            ix = pnt_idx * pnt_data_size
            x = struct.pack(self.timepack, *bindata[ix: ix + self.timesize])
            [time] = struct.unpack(self.timetype, x)
            data[0].append(time)
            ix += self.timesize
            for iy in range(1, self.var_cnt):
                y = struct.pack(self.vsigpack, *bindata[ix:ix + self.vsigsize])
                [vsigval] = struct.unpack(self.vsigtype, y)
                data[iy].append(vsigval)
                ix += self.vsigsize

        self.write_data_to_sigfiles(data, pnt_cnt)

        pnt_cnt += bin_pnt_cnt
        bindata = bindata[pnt_data_size * bin_pnt_cnt:]

        return bindata, pnt_cnt


    def parseWavefileData(self, fp):
        if self.large_file and self.plotname == "tr" and self.sigfiles_exist[self.plotname]:
            return
        bindata = []
        readidx = 0
        readsiz = 0
        pnt_data_size = self.timesize + self.vsigsize * (self.var_cnt - 1)
        pnt_cnt = 0
        while(True):
            try:
                nprev  = np.frombuffer(fp.read(4),   dtype="int32")
                limits = np.frombuffer(fp.read(4*4), dtype="int32")
                if len(limits) < 4:
                    break
            except:
                break
            ndat = limits[1]
            dataline = np.frombuffer(fp.read(4*ndat), dtype="B")
            readidx += 1
            readsiz += ndat
            bindata.extend(dataline)

            if self.large_file and self.plotname == "tr":
                bin_pnt_cnt = int(len(bindata) / pnt_data_size)
                if bin_pnt_cnt * self.var_cnt > 16 * 1024 * 1024:
                    # for speedup,
                    # I/O wirte to sigfile is much slower than memory handling
                    # we will accumulate to at least 100 pnts and then do I/O writing
                    bindata, pnt_cnt = self._dump_data_to_sigfiles(bindata, pnt_data_size, pnt_cnt)

        if self.large_file and self.plotname == "tr":
            # write remaining data to sigfiles
            bindata, pnt_cnt = self._dump_data_to_sigfiles(bindata, pnt_data_size, pnt_cnt)
            self.update_sigfiles_pntcnt(pnt_cnt)

            self.pnt_cnt = pnt_cnt
            self.data = None

        else:
            data = []
            nbytes = len(bindata)
            ix = 0
            while True:
                x = struct.pack(self.timepack, *bindata[ix:ix + self.timesize])
                [time] = struct.unpack(self.timetype, x)
                data.append(time)
                ix += self.timesize
                if ix >= nbytes:
                    break

                for iy in range(self.num_cnt -1):
                    x = struct.pack(self.vsigpack, *bindata[ix:ix + self.vsigsize])
                    [vsigval] = struct.unpack(self.vsigtype, x)
                    data.append(vsigval)
                    ix += self.vsigsize
                    if ix >= nbytes:
                        break
            # ------------------------
            # last data entry is 1e30
            # ------------------------
            data.pop()
            assert len(data) % self.num_cnt == 0
            self.pnt_cnt = int(len(data) / self.num_cnt)
            self.data = np.array(data).reshape(self.pnt_cnt, self.num_cnt).transpose()
