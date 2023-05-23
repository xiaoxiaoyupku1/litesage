import os
import numpy as np


def plotnamestr_to_plotname(plotnamestr):
    if plotnamestr.startswith("Transient Analysis"):
        return "tr"
    elif plotnamestr.startswith("DC transfer characteristic"):
        return "dc"
    elif plotnamestr.startswith("AC Analysis"):
        return "ac"
    elif plotnamestr.startswith("Operating Point"):
        return "op"
    else:
        assert 0, "not valid plotname str: {}".format(plotnamestr)

def plotname_to_plotnamestr(plotname):
    if plotname == "tr":
        return "Transient Analysis"
    elif plotname == "op":
        return "Operating Point"
    elif plotname == "dc":
        return "DC transfer characteristic"
    elif plotname == "ac":
        return "AC Analysis"
    else:
        assert 0, "not valid plotname: {}".format(plotname)


# a container for name:value
class NamedVal():
    def __init__(self, name="", value=0.0):
        self._name = name
        self._value = value
    def __lt__(self, other):
        return self._value < other._value
    def __repr__(self):
        return "{}:{}".format(self._name, self._value)



def calcTopDiff(array0, array1, signames, top):
    assert array0.shape == array1.shape, "array shape not match: {} {}".format(array0.shape, array1.shape)
    assert array0.ndim == 2, "not correct array0 ndim = {}".format(array0.ndim)
    assert array0.shape[0] == len(signames), "sig size not match with array size: {} {}".format(len(signames), array0.shape[0])
    if np.allclose(array0, array1, atol=1e-15):
        return [], []

    reldiffs = []
    absdiffs = []
    for sigidx, signame in enumerate(signames):
        val0 = array0[sigidx, :]
        val1 = array1[sigidx, :]
        absdiff = np.absolute(val1 - val0)
        reldiff = np.max(absdiff / (np.absolute(val0) + 1.0e-12))
        absdiff = np.max(absdiff)
        reldiffs.append(NamedVal(signame, reldiff))
        absdiffs.append(NamedVal(signame, absdiff))

    reldiffs.sort(reverse=True)
    reldiffs = reldiffs[:top]
    absdiffs.sort(reverse=True)
    absdiffs = absdiffs[:top]
    return absdiffs, reldiffs


def get_wavefile_format(wavefile):
    """
    support wavefile format of:
    1. HSPICE bin
    2. HSPICE txt
    3. HSPICE ic0
    3. nutmeg, e.g., ngspice, FoohuSpice
    4. psf, TODO

    """
    if not os.path.isfile(wavefile):
        print("  ****warning**** file {} not exist".format(wavefile))
        return None
    with open(wavefile, "rb") as fp:
        bs = np.frombuffer(fp.read(16), dtype="int8")
        # hsp bin: [4, 0, 0, 0, 46, 0, 0, 0, 4, 0, 0, 0, 112, 1, 0, 0]
        # psf bin: [0, 0, 4, 0, 0, 0, 0, 21, 0, 0, 2, 80, 0, 0, 0, 33]
        bs = list(bs)
        # print("wavefile = {}, bs = {}".format(wavefile, str(bs)))
        if bs[:4] == [4, 0, 0, 0]:
            return "hspice_bin"
        elif bs[:4] == [0, 0, 5, 0] or \
                bs[:4] == [0, 0, 4, 0] or \
                bs[:4] == [0, 0, 3, 0] or \
                bs[:4] == [0, 0, 2, 0]:
            return "psf_bin"
        # for b in bs:
        #     # for nutmeg, the first line is Title: ...,
        #     # it may very short and will have \n in the first 16 int
        #     if (b < 32 and b != 10) or b > 127:
        #         return "hspice_bin"

        # Plotname in wavefile, then it is nutmeg, e.g., ngspice, foohu spice
        fp.seek(0, 0)
        while True:
            try:
                line = fp.readline().decode("ascii")
                if line == "":
                    break
                line = line.strip()
                if line.startswith("Plotname:"):
                    return "nutmeg"
                if line.startswith(".nodeset") or line.startswith(".ic"):
                    return "hspice_ic0"
                if "$&%#" in line:
                    return "hspice_txt"
                if '"PSFversion"' in line:
                    return "psf_txt"
            except UnicodeDecodeError as err:
                print(err)
                print("    ****error**** not valid wavefile: {}".format(wavefile))
                return None
        assert 0, "  ****error****not supported wavefile format: {}".format(wavefile)

    return None
