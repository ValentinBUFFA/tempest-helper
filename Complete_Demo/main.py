from helpers import bcolors
from energy_det import *
from save_trace import *
from frame_correlate import *

import argparse
from argparse import RawTextHelpFormatter


##################################################
# Functions calling python modules
##################################################


def clear_files(folder_path="traces/"):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    for entry in os.scandir(folder_path):
        os.remove(entry.path)


def get_candidates(sdr, path_to_src, verbose=False):
    qapp = Qt.QApplication(sys.argv)

    tb = energy_detection(verbose, sdr=sdr, path_to_src=path_to_src)
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()


def save_traces(sdr, folder_path="traces/"):
    for mode, frq in zip(candidate_modes, candidate_freqs):
        tb = trace_to_file(os.path.join(folder_path, mode + ".trace"), frq, sdr=sdr)
        tb.start()
        time.sleep(0.5)
        tb.stop()
        tb.wait()


def parsing_args():
    parser = argparse.ArgumentParser(
        description="Automatic resolution and refresh rate finder for TEMPEST",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--folder",
        default="traces/",
        help="path to where traces will be saved/searched (default: traces/)",
    )
    parser.add_argument(
        "--skip-record",
        help="skip steps 1 and 2 and look in FOLDER for traces to process",
        action="store_true",
    )
    parser.add_argument(
        "--sdr",
        default="hackrf",
        help='choose between "usrp" or "hackrf" (default: hackrf)',
    )
    parser.add_argument(
        "--step",
        help="explore until the desired step is reached (default: 3)\n1 - energy detection\n2 - save traces\n3 - correlation on frames\n4 - correlation on lines",
        metavar="1-4",
        default=3,
        type=int,
    )
    parser.add_argument(
        "--custom-list",
        help="path to a file containing two python lists for modes and frequencies",  #! TODO
        default="modes.txt",
    )
    return parser.parse_args()


##################################################
# Main function
##################################################

if __name__ == "__main__":
    args = parsing_args()

    # Computation part
    if args.skip_record:
        args.step -= 2
    else:
        print(
            f"\n{bcolors.UNDERLINE}{bcolors.HEADER}STEP 1 - Listening at usual frequencies to get the best candidates{bcolors.ENDC}\n"
        )
        get_candidates(
            verbose=args.verbose, sdr=args.sdr, path_to_src=args.custom_list
        )  # Measure energy leakage
        args.step -= 1

        if args.step > 0:
            print(
                f"\n{bcolors.UNDERLINE}{bcolors.HEADER}STEP 2 - Saving traces of each candidate{bcolors.ENDC}\n"
            )
            clear_files(
                folder_path=args.folder
            )  # Deleting the files with least leakage
            print(f"GNU Radio will restart {len(candidate_freqs)} times")
            save_traces(
                folder_path=args.folder, sdr=args.sdr
            )  # Saving energy leakage in files
            args.step -= 1

    if args.step > 0:
        print(
            f"\n{bcolors.UNDERLINE}{bcolors.HEADER}STEP 3 - Correlation on successive frames{bcolors.ENDC}\n"
        )
        correlate_folder(
            folder_path=args.folder, verbose=args.verbose
        )  # Correlation computation
        args.step -= 1

    if args.step > 0:
        print(
            f"\n{bcolors.UNDERLINE}{bcolors.HEADER}STEP 4 - Correlation on successive lines {bcolors.FAIL}[NOT IMPLEMENTED YET]{bcolors.ENDC}\n"
        )
        #! TODO correlation on lines
        args.step -= 1
