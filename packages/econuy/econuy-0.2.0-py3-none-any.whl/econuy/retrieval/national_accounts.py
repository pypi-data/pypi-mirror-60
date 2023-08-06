import datetime as dt
from os import PathLike
from typing import Union

import pandas as pd
from pandas.tseries.offsets import MonthEnd

from econuy.processing import freqs, convert
from econuy.resources import updates, columns
from econuy.resources.lstrings import nat_accounts_metadata


def get(update_dir: Union[str, PathLike, bool] = False, revise_rows: int = 0,
        save_dir: Union[str, PathLike, bool] = False,
        force_update: bool = False):
    """Get national accounts data.

    Parameters
    ----------
    update_dir : str, PathLike or bool (default is False)
        Path, path-like string pointing to a directory for updating, or bool,
        in which case if True, save in predefined file, or False, don't update.
    revise_rows : int (default is 0)
        How many rows of old data to replace with new data.
    save_dir : str, PathLike or bool (default is False)
        Path, path-like string pointing to a directory for saving, or bool,
        in which case if True, save in predefined file, or False, don't save.
    force_update : bool (default is False)
        If True, fetch data and update existing data even if it was modified
        within its update window (for national accounts, 80 days)

    Returns
    -------
    parsed_excels : dictionary of Pandas dataframes
        Each dataframe corresponds to a national accounts table.

    """
    update_threshold = 80

    parsed_excels = {}
    for file, metadata in nat_accounts_metadata.items():

        if update_dir is not False:
            update_path = updates._paths(update_dir, multiple=True,
                                         multname=metadata["Name"])
            delta, previous_data = updates._check_modified(update_path)

            if delta < update_threshold and force_update is False:
                print(f"{metadata['Name']}.csv was modified within"
                      f" {update_threshold} day(s). Skipping download...")
                parsed_excels.update({metadata["Name"]: previous_data})
                continue

        raw = pd.read_excel(file, skiprows=9, nrows=metadata["Rows"])
        proc = (raw.drop(columns=["Unnamed: 0"]).
                dropna(axis=0, how="all").dropna(axis=1, how="all"))
        proc = proc.transpose()
        proc.columns = metadata["Colnames"]
        proc.drop(["Unnamed: 1"], inplace=True)

        _fix_dates(proc)

        if metadata["Index"] == "No":
            proc = proc.divide(1000)
        if update_dir is not False:
            proc = updates._revise(new_data=proc, prev_data=previous_data,
                                   revise_rows=revise_rows)
        proc = proc.apply(pd.to_numeric, errors="coerce")

        columns._setmeta(proc, area="Actividad económica", currency="UYU",
                         inf_adj=metadata["Inf. Adj."],
                         index=metadata["Index"],
                         seas_adj=metadata["Seas"], ts_type="Flujo",
                         cumperiods=1)

        if save_dir is not False:
            save_path = updates._paths(save_dir, multiple=True,
                                       multname=metadata["Name"])
            proc.to_csv(save_path)

        parsed_excels.update({metadata["Name"]: proc})

    return parsed_excels


def _fix_dates(df):
    """Cleanup dates inplace in BCU national accounts files."""
    df.index = df.index.str.replace("*", "")
    df.index = df.index.str.replace(r"\bI \b", "3-", regex=True)
    df.index = df.index.str.replace(r"\bII \b", "6-", regex=True)
    df.index = df.index.str.replace(r"\bIII \b", "9-", regex=True)
    df.index = df.index.str.replace(r"\bIV \b", "12-", regex=True)
    df.index = pd.to_datetime(df.index, format="%m-%Y") + MonthEnd(1)


def _lin_gdp(update: Union[str, PathLike, bool] = False,
             save: Union[str, PathLike, bool] = False,
             force_update: bool = False):
    """Get nominal GDP data in UYU and USD with forecasts.

    Update nominal GDP data for use in the `convert.pcgdp()` function.
    Get IMF forecasts for year of last available data point and the next
    year (for example, if the last period available at the BCU website is
    september 2019, fetch forecasts for 2019 and 2020).

    Parameters
    ----------
    update : str, PathLike or bool (default is False)
        Path, path-like string pointing to a CSV file for updating, or bool,
        in which case if True, save in predefined file, or False, don't update.
    save : str, PathLike or bool (default is False)
        Path, path-like string pointing to a CSV file for saving, or bool,
        in which case if True, save in predefined file, or False, don't saving.
    force_update : bool (default is False)
        If True, fetch data and update existing data even if it was modified
        within its update window (for national accounts data, 80 days)

    Returns
    -------
    output : Pandas dataframe
        Quarterly GDP in UYU and USD with 1 year forecasts.

    """
    update_threshold = 80

    if update is not False:
        update_path = updates._paths(update, multiple=False, name="lin_gdp.csv")
        delta, previous_data = updates._check_modified(update_path)

        if delta < update_threshold and force_update is False:
            print(f"{update} was modified within {update_threshold} day(s). "
                  f"Skipping download...")
            return previous_data

    data_uyu = get(update_dir=True, revise_rows=4, save_dir=True,
                   force_update=False)["na_gdp_cur_nsa"]
    data_uyu = freqs.rolling(data_uyu, periods=4, operation="sum")
    data_usd = convert.usd(data_uyu)

    data = [data_uyu, data_usd]
    last_year = data_uyu.index.max().year
    if data_uyu.index.max().month == 12:
        last_year += 1

    results = []
    for table, gdp in zip(["NGDP", "NGDPD"], data):

        table_url = (f"https://www.imf.org/external/pubs/ft/weo/2019/02/weodat"
                     f"a/weorept.aspx?sy={last_year-1}&ey={last_year+1}&scsm=1"
                     f"&ssd=1&sort=country&ds=.&br=1&pr1.x=27&pr1.y=9&c=298&s"
                     f"={table}&grp=0&a=")
        imf_data = pd.to_numeric(pd.read_html(table_url)[4].iloc[2, [5, 6, 7]])
        imf_data = imf_data.reset_index(drop=True)
        fcast = (gdp.loc[[dt.datetime(last_year-1, 12, 31)]].
                 multiply(imf_data.iloc[1]).divide(imf_data.iloc[0]))
        fcast = fcast.rename(index={dt.datetime(last_year-1, 12, 31):
                                    dt.datetime(last_year, 12, 31)})
        next_fcast = (gdp.loc[[dt.datetime(last_year-1, 12, 31)]].
                      multiply(imf_data.iloc[2]).divide(imf_data.iloc[0]))
        next_fcast = next_fcast.rename(index={dt.datetime(last_year-1, 12, 31):
                                              dt.datetime(last_year+1, 12, 31)})
        fcast = fcast.append(next_fcast)
        gdp = gdp.append(fcast)
        results.append(gdp)

    output = pd.concat(results, axis=1)
    output = output.resample("Q-DEC").interpolate("linear")

    if save is not False:
        save_path = updates._paths(save, multiple=False, name="lin_gdp.csv")
        output.to_csv(save_path)

    return output
