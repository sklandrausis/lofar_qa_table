import sys
import os
import argparse
import math
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from multiprocessing import Process
from read_solution_files import SolutionFileInfo


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Prints information about prefactor calibrator solution files. ''')
    parser.add_argument('solution_file_directory', type=str, help='Specify the directory of solution files.')
    parser.add_argument('output_file_directory', type=str, help='Specify the output directory.')
    parser.add_argument("-v", "--version", action="version", version='%(prog)s - Version 1.0')
    arguments = parser.parse_args()
    return arguments


def create_results_directory(s_id):
    result_directory = "results_" + s_id
    if not os.path.exists(result_directory):
        os.mkdir(result_directory)


def run_process(function, *arguments):
    p = Process(target=function, args=(*arguments,))
    p.start()
    p.join()


def plot_bandpass(bandpass_frequency, bandpass_value, weight, station_names, rows, columns, s_id, output_directory):
    f = plt.figure(figsize=(10, 10))
    s = 0.5

    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        a = min(max(bandpass_value[0, :, station_names.index(stations_name), 0]),
                max(bandpass_value[0, :, station_names.index(stations_name), 1]))
        time_points = len(bandpass_value[:, :, station_names.index(stations_name), 0])
        b_x = np.nan_to_num(sum(bandpass_value[:, :, station_names.index(stations_name), 0]) / time_points) * \
              (sum(np.nan_to_num(weight)[:, :, station_names.index(stations_name), 0]) / time_points)

        b_y = np.nan_to_num(sum(bandpass_value[:, :, station_names.index(stations_name), 1]) / time_points) * \
              (sum(np.nan_to_num(weight)[:, :, station_names.index(stations_name), 1]) / time_points)

        plt.scatter(bandpass_frequency, b_x, s)
        plt.scatter(bandpass_frequency, b_y, s)
        plt.text(30, a, stations_name.decode('UTF-8'))
        plt.xlabel("frequency [MHz]")
        plt.ylabel("amplitude")
    f.tight_layout()
    plt.savefig(output_directory + "/results_" + s_id + "/" + "bandpass.png")


def plot_bandpass2(bandpass_frequency, time, bandpass_value, weight, station_names, rows, columns, s_id):
    time = Time(time / 60 / 60 / 24, format='mjd').value
    a = max(bandpass_frequency) - 10
    b = min(time) + 10
    xx, yy = np.meshgrid(Time(time / 60 / 60 / 24, format='mjd').value, bandpass_frequency)

    f1 = plt.figure(figsize=(50, 50))
    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z1 = bandpass_value[:, :, station_names.index(stations_name), 0] * weight[:, :, station_names.index(stations_name), 0]
        z1_new = np.nan_to_num(z1.transpose())
        plt.text(b, a, stations_name.decode('UTF-8'), size='large', color="r")
        c1 = plt.contourf(xx, yy, z1_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f1.colorbar(c1, cax=f1.add_axes([0.935, 0.155, 0.05, 0.7]))
    f1.tight_layout()
    f1.savefig("results_" + s_id + "/" + "bandpass_xx.png")

    f2 = plt.figure(figsize=(50, 50))
    for stations_name in station_names:
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z2 = bandpass_value[:, :, station_names.index(stations_name), 1] * weight[:, :, station_names.index(stations_name), 1]
        z2_new = np.nan_to_num(z2.transpose())
        plt.text(b, a, stations_name.decode('UTF-8'), size='large', color="r")
        c2 = plt.contourf(xx, yy, z2_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f2.colorbar(c2, cax=f2.add_axes([0.935, 0.155, 0.05, 0.7]))
    f2.tight_layout()
    f2.savefig(output_directory + "/results_" + s_id + "/" + "bandpass_yy.png")


def plot_bandpass3(bandpass_frequency, time, bandpass_value, weight, station_names, rows, columns, s_id, output_directory):
    time = Time(time / 60 / 60 / 24, format='mjd').value
    a = max(bandpass_frequency) - 10
    b = min(time) + 10
    xx, yy = np.meshgrid(Time(time / 60 / 60 / 24, format='mjd').value, bandpass_frequency)

    f1 = plt.figure(figsize=(50, 50))
    for stations_name in station_names:
        time_points = len(bandpass_value[:, :, station_names.index(stations_name), 0])
        b_x = sum(bandpass_value[:, :, station_names.index(stations_name), 0]) / time_points
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z1 = bandpass_value[:, :, station_names.index(stations_name), 0] * weight[:, :, station_names.index(stations_name), 0]
        z1_new = np.nan_to_num(z1.transpose() - b_x[:, None])
        plt.text(b, a, stations_name.decode('UTF-8'), size='large', color="r")
        c1 = plt.contourf(xx, yy, z1_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f1.colorbar(c1, cax=f1.add_axes([0.935, 0.155, 0.05, 0.7]))
    f1.tight_layout()
    f1.savefig("results_" + s_id + "/" + "bandpass3_xx.png")

    f2 = plt.figure(figsize=(50, 50))
    for stations_name in station_names:
        time_points = len(bandpass_value[:, :, station_names.index(stations_name), 1])
        b_y = sum(bandpass_value[:, :, station_names.index(stations_name), 1]) / time_points
        plt.subplot(rows, columns, station_names.index(stations_name) + 1)
        z2 = bandpass_value[:, :, station_names.index(stations_name), 1] * weight[:, :, station_names.index(stations_name), 1]
        z2_new = np.nan_to_num(z2.transpose() - b_y[:, None])
        plt.text(b, a, stations_name.decode('UTF-8'), size='large', color="r")
        c2 = plt.contourf(xx, yy, z2_new)
        plt.xlabel("time [MJD]")
        plt.ylabel("frequency [MHz]")

    f2.colorbar(c2, cax=f2.add_axes([0.935, 0.155, 0.05, 0.7]))
    f2.tight_layout()
    f2.savefig(output_directory + "/results_" + s_id + "/" + "bandpass3_yy.png")


def main(solution_file_dir, output_directory):
    solution_files = [SolutionFileInfo(solution_file_dir + "/" + s) for s in os.listdir(solution_file_dir)]
    max_columns = 8

    def run_all_operations():
        run_process(create_results_directory, sas_id)
        run_process(plot_bandpass, frequency, value, weight, stations_names, rows, columns, sas_id, output_directory)
        run_process(plot_bandpass2, frequency, time, value, weight, stations_names, rows, columns, sas_id, output_directory)
        run_process(plot_bandpass3, frequency, time, value, weight, stations_names, rows, columns, sas_id, output_directory)

    for solution_file in solution_files:
        sas_id = solution_file.get_sas_id
        frequency = solution_file.get_bandpass["frequency"]
        value = solution_file.get_bandpass["value"]
        weight = solution_file.get_weight
        time = solution_file.get_time
        stations_names = list(set([s[0] for s in solution_file.get_stations]))
        nr_stations = len(stations_names)
        if nr_stations <= max_columns:
            rows = 1
            columns = nr_stations
        else:
            columns = max_columns
            rows = math.ceil(nr_stations / max_columns)

        run_process(run_all_operations)

    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    solution_file_directory = args.solution_file_directory
    output_directory = args.output_file_directory
    main(solution_file_directory, output_directory)
