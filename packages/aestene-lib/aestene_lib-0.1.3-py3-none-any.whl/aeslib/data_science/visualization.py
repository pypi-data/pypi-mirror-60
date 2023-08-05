"""Functions for visualization purposes in Data Science tasks.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_heatmap_between_columns(
        df: pd.DataFrame,
        size: tuple = (7, 7),
        savefig=False,
        path_and_file_name='heatmap') -> plt.axes:
    """Plot heatmap between values of multiple columns in a Pandas dataframe.
    Requires that there are no NaN values in the dataframe.

    Arguments:
        df {pd.DataFrame} -- Pandas dataframe
        size {tuple} -- Size of output figure

    Keyword Arguments:
        savefig {bool} -- True to save figure (default: {False})
        path_and_file_name {str} -- Filepath (default: {'heatmap'})

    Returns:
        plt.axes -- Matplotlib axes object
    """
    plt.figure(figsize=size)

    axes = sns.heatmap(df, vmin=-1, cmap='coolwarm', annot=True)

    if savefig:
        plt.savefig(path_and_file_name)

    return axes
