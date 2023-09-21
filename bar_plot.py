import numpy as np
import matplotlib.pyplot as plt
from summarize import get_e2e_latency_numbers, get_latency_numbers, remove_first_x_percent

category_names = ["User->Kernel", "Kernel->NIC", "NIC->NIC", "NIC->Kernel", "Kernel->User",]
results = {
    'Latency': [10, 15, 17, 32, 26]
}


nic_kernel, nic_user, kernel_user = get_latency_numbers("latancy.txt")
e2e = get_e2e_latency_numbers("end_to_end_latency.txt")

nic_kernel = remove_first_x_percent(10, nic_kernel)
nic_user = remove_first_x_percent(10, nic_user)
kernel_user= remove_first_x_percent(10, kernel_user)
e2e = remove_first_x_percent(10, e2e)

array = np.array(nic_user)
nic_user = int(np.percentile(array, 50))
array = np.array(nic_kernel)
nic_kernel = int(np.percentile(array, 50))
array = np.array(e2e)
e2e = int(np.percentile(array, 50))

results["Latency"][0] = nic_user-nic_kernel
results["Latency"][1] = nic_kernel
results["Latency"][2] = e2e-2*nic_user
results["Latency"][3] = nic_kernel
results["Latency"][4] = nic_user-nic_kernel


def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax


survey(results, category_names)
plot_name = "bar_plot.png"
plt.gcf().set_size_inches(10, 3)
plt.savefig(plot_name, dpi=300)

