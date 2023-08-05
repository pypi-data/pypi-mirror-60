from .utils import load_dataset

def get_monthly_mean(df, datecolname="Date"):
    """Return the monthly mean of each columns of a dataframe

    It does not modify the input dataframe.

    Parameters
    ----------

    df : pd.DataFrame
        the dataframe
    datecolname : str, default 'Date',
        the name of the date column

    Returns
    -------

    dftmp : pd.DataFrame with a "month" column
    dfmean : pd.DataFrame with the monthly mean of each column

    """
    dftmp = df.copy()
    dftmp["month"] = dftmp[datecolname].apply(lambda x: x.month)
    dftmp = dftmp.groupby("month")
    dfmean = dftmp.mean()
    return (dftmp, dfmean)


def get_monthly_mean_relative(dfi, datecolname="Date"):
    """Return the monthly mean relative value of each column of a DataFrame

    Parameters
    ----------

    df : pd.DataFrame
    datecolname : str, default 'Date'

    Returns
    -------

    dfrel : pd.DataFrame
    """
    df, dfmean = get_monthly_mean(dfi)
    dfrel = (dfmean.T / dfmean.sum(axis=1)).T
    return dfrel


def get_mean_intrinsic_OP(dfopi, OPtype):
    """Get the mean intrinsic OP per factor
    
    Parameters
    ----------

    dfopi : pd.DataFrame
    OPtype : str

    Returns
    -------

    pd.Serie : mean OPi per factor
    """
    return dfopi.groupby("Factor").mean()[OPtype]


def explode_pm_to_src(dfrel, dfpm, datecolname="Date", pm10colname="PM10"):
    """Return the proportion of each source for a given PM timeserie

    Parameters
    ----------

    dfrel : pd.DataFrame
        Monthly relative contribution of each sources.
    dfpm : pd.DataFrame
        PM concentration timeserie, with a date column
    datecolname : str, default 'Date'
        Name of the date column in dfpm
    pm10colname : str, default 'PM10'
        Name of the PM column in dfpm

    Returns
    -------

    dfpm_bysrc : pd.DataFrame with the absolute contribution of the sources as
        new columns
    """
    dfpm_bysrc = dfpm.copy()
    dfpm_bysrc["month"] = dfpm_bysrc[datecolname].apply(lambda x: x.month)
    for c in dfrel.columns:
        for m in range(1, 13):
            idx = dfpm_bysrc["month"] == m
            dfpm_bysrc.loc[idx, c] = dfpm_bysrc.loc[idx, pm10colname] * dfrel.loc[m, c]
            if c == "Unnamed: 0":
                print(c)
    return dfpm_bysrc


def get_op_from_src(df, meanopi):
    """Compute the OP apportioned by each source

    Parameters
    ----------

    df : pd.DataFrame
        Timeserie of the source contribution to the mass
    meanopi : pd.Serie
        Mean OPi per source

    Returns
    -------

    dfop : pd.DataFrame
        Timeserie of the source contribution to the OP
    """
    dfop = df.copy()
    for i in meanopi.index:
        if i in dfop.columns:
            dfop[i] = dfop[i] * meanopi.loc[i]
    return dfop


def get_op_from_pm10(dfpm, OPtype, datecolname="Date", pm10colname="PM10",
    dfsrc=None, sources=None, dfopi=None):
    """Return the OP contribution from a given PM10 time serie


    Parameters
    ----------

    dfpm : pd.DataFrame
        Timeserie of PM concentration, with a date and PM column specified with
        `datecolname` and `pm10colname`
    OPtype : str, ["AAv", "DTTv"]
        The given OP we want to predict
    datecolname : str, default 'Date'
        The date column name of dfpm
    pm10colname : str, default 'PM10'
        The PM concentration column name of dfpm

    dfsrc : pd.DataFrame, default to the one provided by load_dataset("src.csv")
        Timeserie of source contribution from a ensemble of site. It should have at least a 'Date' column.
    sources : list of str, default to the one provided by load_dataset("common_sources.csv")
        The name of the sources to take into account
    dfopi : pd.DataFrame, default to the one provided by load_dataset("opi.csv")
        Mean intrinsic OP for an ensemble of source

    Returns
    -------
    """
    if dfsrc is None:
        dfsrc = load_dataset("src")
    if sources is None:
        sources = load_dataset("common_sources")
        sources = list(sources.loc[sources["is_common"], "Factor"])
    if dfopi is None:
        dfopi = load_dataset("opi")

    meanopi = get_mean_intrinsic_OP(dfopi, OPtype)

    # Restrict to the sources provided
    dfsrc = dfsrc[["Date"] + sources]
    meanopi = meanopi.loc[sources]

    dfrel = get_monthly_mean_relative(dfsrc)
    dfpm_bysrc = explode_pm_to_src(dfrel, dfpm, datecolname=datecolname, pm10colname=pm10colname)
    dfop = get_op_from_src(dfpm_bysrc, meanopi)
    dfop["totalOP"] = dfop[sources].sum(axis=1)
    return dfop
