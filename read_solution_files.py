import sys
import os
import argparse
import h5py
from astropy.time import Time


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Prints information about prefactor calibrator solution files. ''')
    parser.add_argument('solution_file_directory', type=str, help='Specify the directory of solution files.')
    parser.add_argument("-v", "--version", action="version", version='%(prog)s - Version 1.0')
    arguments = parser.parse_args()
    return arguments


class SolutionFileInfo:

    def __init__(self, file):
        self.file = file
        file = h5py.File(self.file, 'r')
        self.sas_id = self.file.split("/")[-1].split("_")[0].replace("L", "")
        self.data = file["calibrator"]

    @property
    def get_data(self):
        return self.data

    @property
    def get_sas_id(self):
        return self.sas_id

    @property
    def get_stations(self):
        return self.get_data["antenna"].value

    @property
    def get_bandpass(self):
        bandpass = self.get_data["bandpass"]
        bandpass_frequency = bandpass["freq"].value / 1e+6
        bandpass_value = bandpass["val"].value
        return {"bandpass": bandpass, "frequency": bandpass_frequency, "value": bandpass_value}

    @property
    def get_time(self):
        return self.get_bandpass["bandpass"]["time"].value

    @property
    def get_start_time(self):
        return str(Time(self.get_time[0]/60/60/24, format='mjd').to_datetime())

    @property
    def get_end_time(self):
        return str(Time(self.get_time[-1]/60/60/24, format='mjd').to_datetime())

    @property
    def get_duration(self):
        assert isinstance(self.get_start_time, object)
        return self.get_time[-1] - self.get_time[0]


def main(solution_file_dir):
    solution_files = [SolutionFileInfo(solution_file_dir + "/" + s) for s in os.listdir(solution_file_dir)]

    for solution_file in solution_files:
        print("SAS ID: ", solution_file.get_sas_id,
              "Start time: ", solution_file.get_start_time,
              "End time: ", solution_file.get_start_time,
              "Duration: ", solution_file.get_duration)
    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    solution_file_directory = args.solution_file_directory
    main(solution_file_directory)
