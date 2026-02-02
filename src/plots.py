import pandas as pd
import numpy as np


def degree_vs_paths(g):
    degree = (g.in_degrees() + g.out_degrees()).numpy()

    if "path_occurrences" in g.ndata:
        paths = g.ndata["path_occurrences"].numpy()
    else:
        paths = np.zeros_like(degree)

    return pd.DataFrame({
        "log10(Degree + 1)": np.log10(degree + 1),
        "log10(Path occurrences + 1)": np.log10(paths + 1),
    })


def path_occurrences_histogram(g):
    if "path_occurrences" not in g.ndata:
        return None

    paths = g.ndata["path_occurrences"].numpy()
    return (
        pd.Series(paths)
        .value_counts()
        .sort_index()
        .to_frame("count")
    )
