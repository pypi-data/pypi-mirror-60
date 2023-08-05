import os
import pandas as pd

from urllib.request import urlretrieve


def get_data_home(data_home=None):
    """Return the path of the pyOPestimator data directory.
    This is used by the ``load_dataset`` function.
    If the ``data_home`` argument is not specified, the default location
    is ``~/pyOPestimator-data``.
    Alternatively, a different default location can be specified using the
    environment variable ``PYOPESTIMATOR_DATA``.
    """
    if data_home is None:
        data_home = os.environ.get('PYOPESTIMATOR_DATA',
                                   os.path.join('~', 'pyOPestimator-data'))
    data_home = os.path.expanduser(data_home)
    if not os.path.exists(data_home):
        os.makedirs(data_home)
    return data_home


def load_dataset(name, cache=True, data_home=None, **kws):
    """Load a dataset from the online repository (requires internet).

    Parameters
    ----------
    name : str
        Name of the dataset (`name`.csv on
        https://gricad-gitlab.univ-grenoble-alpes.fr/pmall/pyopestimator-data).
    cache : boolean, optional
        If True, then cache data locally and use the cache on subsequent calls
    data_home : string, optional
        The directory in which to cache data. By default, uses ~/pyOPestimator-data/
    kws : dict, optional

    """
    path = ("https://gricad-gitlab.univ-grenoble-alpes.fr/"
            "pmall/pyopestimator-data/raw/master/{}.csv")
    full_path = path.format(name)

    if cache:
        cache_path = os.path.join(get_data_home(data_home),
                                  os.path.basename(full_path))
        if not os.path.exists(cache_path):
            urlretrieve(full_path, cache_path)
        full_path = cache_path

    df = pd.read_csv(full_path, **kws)
    if df.iloc[-1].isnull().all():
        df = df.iloc[:-1]

    if name == "src":
        df["Date"] = pd.to_datetime(df["Date"])

    return df
