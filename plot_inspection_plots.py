import sys
import os
import math
import matplotlib.pyplot as plt
from read_solution_files import parse_arguments, SolutionFileInfo


def plot_bandpass(bandpass_frequency, bandpass_value, station_names, rows, columns):
    f = plt.figure(figsize=(15, 15))
    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        a = min(max(bandpass_value[0, :, station_names.index(stations_name), 0]), max(bandpass_value[0, :, station_names.index(stations_name), 1]))
        plt.scatter(bandpass_frequency, bandpass_value[0, :, station_names.index(stations_name), 0])
        plt.scatter(bandpass_frequency, bandpass_value[0, :, station_names.index(stations_name), 1])
        plt.text(30, a, stations_name.decode('UTF-8'))
        plt.xlabel("frequency [MHz]")
        plt.ylabel("amplitude")
    f.tight_layout()
    plt.show()


def main(solution_file_dir):
    solution_files = [SolutionFileInfo(solution_file_dir + "/" + s) for s in os.listdir(solution_file_dir)]
    max_columns = 8

    for solution_file in solution_files:

        frequency = solution_file.get_bandpass["frequency"]
        value = solution_file.get_bandpass["value"]
        stations_names = list(set([s[0] for s in solution_file.get_stations]))
        nr_stations = len(stations_names)
        if nr_stations <= max_columns:
            rows = 1
            columns = nr_stations
        else:
            columns = max_columns
            rows = math.ceil(nr_stations/max_columns)

        plot_bandpass(frequency, value, stations_names, rows, columns)

    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    solution_file_directory = args.solution_file_directory
    main(solution_file_directory)
