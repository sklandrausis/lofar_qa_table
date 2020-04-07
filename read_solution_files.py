import sys
import os
import argparse
import h5py
from astropy.time import Time
import astropy.units as u
from astroplan import Observer
from astropy.coordinates import EarthLocation


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
        return self.get_data["antenna"][()]

    @property
    def get_bandpass(self):
        bandpass = self.get_data["bandpass"]
        bandpass_frequency = bandpass["freq"][()] / 1e+6
        bandpass_value = bandpass["val"][()]
        return {"bandpass": bandpass, "frequency": bandpass_frequency, "value": bandpass_value}

    @property
    def get_time(self):
        return self.get_bandpass["bandpass"]["time"][()]

    @property
    def get_weight(self):
        return self.get_bandpass["bandpass"]["weight"][()]

    @property
    def get_start_time(self):
        return Time(self.get_time[0]/60/60/24, format='mjd')

    @property
    def get_end_time(self):
        return Time(self.get_time[-1]/60/60/24, format='mjd')

    @property
    def get_duration(self):
        assert isinstance(self.get_start_time, object)
        return self.get_time[-1] - self.get_time[0]


def main(solution_file_dir):
    solution_files = [SolutionFileInfo(solution_file_dir + "/" + s) for s in os.listdir(solution_file_dir)]

    for solution_file in solution_files:
        day_type = ""
        CS001LBA_coordinates = solution_file.get_stations[0][1]
        location = EarthLocation.from_geocentric(CS001LBA_coordinates[0]*u.m, CS001LBA_coordinates[1]*u.m, CS001LBA_coordinates[2]*u.m)
        CS001LBA = Observer(location=location, name="CS001LBA", timezone="UTC")

        if CS001LBA.is_night(solution_file.get_start_time):
            day_type = "night"

        elif solution_file.get_start_time < CS001LBA.sun_rise_time(solution_file.get_start_time, which='next'):
            day_type = "dawn"

        elif solution_file.get_start_time > CS001LBA.sun_set_time(solution_file.get_start_time, which='next'):
            day_type = "dusk"

        else:
            day_type = "day"

        print("SAS ID: ", solution_file.get_sas_id,
              "Start time: ", solution_file.get_start_time.to_datetime(),
              "End time: ", solution_file.get_start_time.to_datetime(),
              "Duration: ", solution_file.get_duration, "Seconds",
              "Day type: ", day_type)
    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    solution_file_directory = args.solution_file_directory
    main(solution_file_directory)
