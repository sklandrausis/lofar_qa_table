import sys
import os
import math
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from multiprocessing import Process
from read_solution_files import parse_arguments, SolutionFileInfo


def create_results_directory(s_id):
    result_directory = "results_" + s_id
    if not os.path.exists(result_directory):
        os.mkdir(result_directory)


def run_process(function, *arguments):
    p = Process(target=function, args=(*arguments,))
    p.start()
    p.join()


def plot_bandpass(bandpass_frequency, bandpass_value, station_names, rows, columns, s_id):
    f = plt.figure(figsize=(10, 10))
    s = 0.5

    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        a = min(max(bandpass_value[0, :, station_names.index(stations_name), 0]),
                max(bandpass_value[0, :, station_names.index(stations_name), 1]))
        time_points = len(bandpass_value[:, :, station_names.index(stations_name), 0])
        b_x = sum(bandpass_value[:, :, station_names.index(stations_name), 0]) / time_points
        b_y = sum(bandpass_value[:, :, station_names.index(stations_name), 1]) / time_points
        plt.scatter(bandpass_frequency, b_x, s)
        plt.scatter(bandpass_frequency, b_y, s)
        plt.text(30, a, stations_name.decode('UTF-8'))
        plt.xlabel("frequency [MHz]")
        plt.ylabel("amplitude")
    f.tight_layout()
    plt.savefig("results_" + s_id + "/" + "bandpass.png")


def plot_bandpass2(bandpass_frequency, time, bandpass_value, station_names, rows, columns, s_id):
    time = Time(time/60/60/24, format='mjd').value
    a = 70 #max(bandpass_frequency) - 10
    b = min(time)
    f = plt.figure(figsize=(15, 15))
    xx, yy = np.meshgrid(Time(time/60/60/24, format='mjd').value, bandpass_frequency)
    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z = bandpass_value[:, :, station_names.index(stations_name), 0]
        z_new = z.transpose()
        plt.text(b, a, stations_name.decode('UTF-8'))
        plt.contourf(xx, yy, z_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f.tight_layout()
    plt.savefig("results_" + s_id + "/" + "bandpass_xx.png")

    f = plt.figure(figsize=(15, 15))
    xx, yy = np.meshgrid(Time(time/60/60/24, format='mjd').value, bandpass_frequency)
    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z = bandpass_value[:, :, station_names.index(stations_name), 1]
        z_new = z.transpose()
        plt.text(b, a, stations_name.decode('UTF-8'))
        plt.contourf(xx, yy, z_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f.tight_layout()
    plt.savefig("results_" + s_id + "/" + "bandpass_yy.png")



def main(solution_file_dir):
    solution_files = [SolutionFileInfo(solution_file_dir + "/" + s) for s in os.listdir(solution_file_dir)]
    max_columns = 8

    def run_all_operations():
        run_process(create_results_directory, sas_id)
        run_process(plot_bandpass, frequency, value, stations_names, rows, columns, sas_id)
        run_process(plot_bandpass2, frequency, time, value, stations_names, rows, columns, sas_id)

    for solution_file in solution_files:
        sas_id = solution_file.get_sas_id
        frequency = solution_file.get_bandpass["frequency"]
        value = solution_file.get_bandpass["value"]
        time = solution_file.get_time
        stations_names = list(set([s[0] for s in solution_file.get_stations]))
        nr_stations = len(stations_names)
        if nr_stations <= max_columns:
            rows = 1
            columns = nr_stations
        else:
            columns = max_columns
            rows = math.ceil(nr_stations/max_columns)

        run_process(run_all_operations)

    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    solution_file_directory = args.solution_file_directory
    main(solution_file_directory)
