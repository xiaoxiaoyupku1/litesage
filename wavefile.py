import os
import sys

from utils import get_wavefile_format
from hspWavefile import HspiceTxtWavefileHandler
from hspWavefile import HspiceBinWavefileHandler
from hspWavefile import HspiceIc0WavefileHandler


def get_wavefile_handler(wavefile):
    file_format = get_wavefile_format(wavefile)
    if file_format == "hspice_txt":
        return HspiceTxtWavefileHandler(wavefile)
    elif file_format == "hspice_bin":
        return HspiceBinWavefileHandler(wavefile)
    elif file_format == "hspice_ic0":
        return HspiceIc0WavefileHandler(wavefile)
    # elif file_format == "psf_txt":
    #     return PsfTxtWavefileHandler(wavefile)
    # elif file_format == "psf_bin":
    #     return PsfBinWavefileHandler(wavefile)
    # elif file_format == "nutmeg":
    #     return FoohuWavefileHandler(wavefile)
    else:
        assert 0, "not valid wavefile format: {} {}".format(file_format, wavefile)


def checkWave(file1, file2, top=1, open_in_wv=False):
    file1_fullpath = os.path.abspath(file1)
    file2_fullpath = os.path.abspath(file2)
    if file1_fullpath == file2_fullpath:
        print("  ****warning**** file {} and {} are the same file".format(file1, file2))
        return "pass", ""
    wave1 = get_wavefile_handler(file1)
    wave1.parseWavefile()
    wave2 = get_wavefile_handler(file2)
    wave2.parseWavefile()
    matching, msg = wave2.checkWave(wave1, top, open_in_wv)
    return matching, msg


def _plot_data(signames, array, msg):
    print("")
    print(msg)
    print("data shape: ", array.shape)
    assert array.ndim == 2
    assert array.shape[0] == len(signames)
    print(",".join(signames[:4]))
    sigcnt, pntcnt = array.shape
    for pntidx in range(pntcnt):
        line = "{:5d}".format(pntidx) + ": " + "  ".join(["{:4e}".format(x) for x in array[:4, pntidx]])
        print(line)


if __name__ == "__main__":
    for wavefile in sys.argv[1:]:
        print("")
        print("handling wavefile: {}".format(wavefile))
        fileformat = get_wavefile_format(wavefile)
        handler = get_wavefile_handler(wavefile)
        handler.parseWavefile()
        print("fileformat = ", fileformat)

        for plotname in handler.plotnames:
            signames = handler.get_signames(plotname)
            sigvals = handler.getSigVals(plotname)
            print("signames =", signames)
            print("sigvals = \n", sigvals)
