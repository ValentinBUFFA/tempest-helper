from videotimings import *


# colors for pretty print
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# * TRACE METADATA HELPER
# path to file must look like hresxvres@fps#standard.trace
# a "mode" is hresxvres@fps#standard
def get_fps(path: str):
    return float(path.split("#")[0].split("@")[1].strip())


def get_x(path: str):
    return int(path.split("#")[0].split("x")[0].strip())


def get_y(path: str):
    return int(path.split("#")[0].split("x")[1].split("@")[0].strip())


def get_standard(path: str):
    return path.split("#")[1].strip()


# return a list with all clocks depending on all valid modes
def parse_mode_and_clock(path):
    outfile = open(path, "r")
    data = outfile.readlines()

    standards = ["cvt", "cvt_rb", "cvt_rb2", "dmt", "cea"]
    mode = []
    clock = []
    for line in data:
        # compute pixel clocks for different standards
        #! Pixel clocks computed by the "js" script are rounded
        # pxclocks = videotimings.compute_pxclock(
        #     get_x(line), get_y(line), get_fps(line)
        # )[0]
        # * Let's compute them again
        _, htotals, vtotals = videotimings.compute_pxclock(
            get_x(line), get_y(line), get_fps(line)
        )
        pxclocks = []
        fps = get_fps(line)
        for htot, vtot in zip(htotals, vtotals):
            pxclocks.append(htot * vtot * fps)
        # * DONE! Now clocks should be more precise
        for pxclock, standard in zip(pxclocks, standards):
            # if existant, append to the list to check
            if pxclock != 0:
                mode.append(line.replace("\n", "") + "#" + standard)
                clock.append(int(pxclock))

    return clock, mode


def get_htot_vtot(path: str):
    standards = ["cvt", "cvt_rb", "cvt_rb2", "dmt", "cea"]
    _, htotals, vtotals = videotimings.compute_pxclock(
        get_x(path), get_y(path), get_fps(path)
    )
    idx = standards.index(get_standard(path))
    return htotals[idx], vtotals[idx]
