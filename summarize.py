import tarfile, json
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from os.path import exists


def get_latency_numbers(filename):
    nic_kernel = []
    nic_user = []
    kernel_user = []

    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.split(",")
            nic_user.append(int(line[0]))
            nic_kernel.append(int(line[1]))
            kernel_user.append(int(line[2]))

    return nic_kernel, nic_user, kernel_user

def get_e2e_latency_numbers(filename):
    e2e = []

    with open(filename, "r") as f:
        for line in f.readlines():
            e2e.append(int(line))

    return e2e

def remove_first_x_percent(x, numbers):
    total = len(numbers)
    ten_percent = int(total/10)
    numbers = numbers[ten_percent:total-1]
    return numbers

def remove_last_x_percent(x, numbers):
    total = len(numbers)
    ten_percent = int(total/10)
    numbers = numbers[0:total-ten_percent-1]
    return numbers

def plot():
    plt.clf()
    plt.cla()
    plt.close()

    if not exists("latency.txt"):
        println("latency.txt does not exists");
        return

    nic_kernel, nic_user, kernel_user = get_latency_numbers("latency.txt")
    e2e_exists = exists("end_to_end_latency.txt")
    if e2e_exists:
        e2e = get_e2e_latency_numbers("end_to_end_latency.txt")


    moving_average=25
    if moving_average != 0:
        nic_kernel = np.convolve(nic_kernel, np.ones(moving_average)/moving_average)
        nic_user = np.convolve(nic_user, np.ones(moving_average)/moving_average)
        kernel_user = np.convolve(kernel_user, np.ones(moving_average)/moving_average)
        if e2e_exists:
            e2e = np.convolve(e2e, np.ones(moving_average)/moving_average)

    nic_kernel = remove_first_x_percent(10, nic_kernel)
    nic_user = remove_first_x_percent(10, nic_user)
    kernel_user= remove_first_x_percent(10, kernel_user)

    if e2e_exists:
        e2e = remove_first_x_percent(10, e2e)
        e2e = remove_last_x_percent(1, e2e)
        plt.plot(e2e, linewidth=0.5, label="End to End")

    nic_kernel = remove_last_x_percent(1, nic_kernel)
    nic_user = remove_last_x_percent(1, nic_user)
    kernel_user= remove_last_x_percent(1, kernel_user)



    plt.plot(nic_user, linewidth=0.5, label="Nic -> user")
    plt.plot(nic_kernel, linewidth=0.5, label="Nic -> Kernel")
    plt.plot(kernel_user, linewidth=0.5, label="Kernel -> User")

    plt.legend(loc="upper left")

    plt.title("Latency from NIC -> User Space")

    plt.xlabel("Packet")
    plt.ylabel("Latency in ns")
    plt.ticklabel_format(scilimits=(-5, 8))

    array = np.array(nic_user)
    median_ns = int(np.percentile(array, 50))
    median_us = int(np.percentile(array, 50) / 1000)
    res_at_10p_ns = int(np.percentile(array, 10))
    res_at_99p_ns = int(np.percentile(array, 99))
    res_at_95p_ns = int(np.percentile(array, 95))
    summary = "NIC->User\n"
    summary += "Median: {}ns ({}us)\n95%: {}ns\n99%: {}ns\n10%: {}ns".format(median_ns, median_us, res_at_95p_ns, res_at_99p_ns, res_at_10p_ns)

    array = np.array(kernel_user)
    median_ns = int(np.percentile(array, 50))
    median_us = int(np.percentile(array, 50) / 1000)
    res_at_10p_ns = int(np.percentile(array, 10))
    res_at_99p_ns = int(np.percentile(array, 99))
    res_at_95p_ns = int(np.percentile(array, 95))
    summary += "\n\nKernel->User\n"
    summary += "Median: {}ns ({}us)\n95%: {}ns\n99%: {}ns\n10%: {}ns".format(median_ns, median_us, res_at_95p_ns, res_at_99p_ns, res_at_10p_ns)

    if e2e_exists:
        array = np.array(e2e)
        median_ns = int(np.percentile(array, 50))
        median_us = int(np.percentile(array, 50) / 1000)
        res_at_10p_ns = int(np.percentile(array, 10))
        res_at_99p_ns = int(np.percentile(array, 99))
        res_at_95p_ns = int(np.percentile(array, 95))
        summary += "\n\nEnd-to-End\n"
        summary += "Median: {}ns ({}us)\n95%: {}ns\n99%: {}ns\n10%: {}ns".format(median_ns, median_us, res_at_95p_ns, res_at_99p_ns, res_at_10p_ns)

    ax = plt.gca()
    ax.set_ylim(ymin=0)
    ax.set_transform(ax.transAxes)
    ax.text(0.95, 0.95, summary,
            horizontalalignment='right',
            verticalalignment='top',color='black',bbox=dict(facecolor='white', alpha=0.3),size=10,
            transform=ax.transAxes)

    plot_name = "plot.png"
    plt.gcf().set_size_inches(10, 5)
    plt.savefig(plot_name, dpi=300)

    print("DONE")

if __name__ == "__main__":
    plot()

