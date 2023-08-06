from typing import List, Tuple
import pandas as pd
from pandas import DataFrame


def filter_by_ranges(
    data: DataFrame, filter_column: str, ranges: List[Tuple[float, float]]
) -> DataFrame:

    frames = []

    for r in ranges:
        frames.append(data[data[filter_column].between(r[0], r[1])])

    return pd.concat(frames)


def get_ranges(
    data: DataFrame, from_column: str, to_column: str
) -> List[Tuple[float, float]]:
    return list(zip(data[from_column], data[to_column]))


def get_data_frame_from_file(filepath: str) -> DataFrame:
    try:
        if ".csv" in filepath.lower():
            # Assume that the user uploaded a CSV file
            return pd.read_csv(filepath)
        elif ".xls" in filepath.lower():
            # Assume that the user uploaded an excel file
            return pd.read_excel(filepath)
    except Exception as e:
        raise Exception("{} couldn't be parsed error: {}".format(filepath, str(e)))


def filter_data_by_ranges_from_file(
    data_file: str,
    filter_file: str,
    from_column: str,
    to_column: str,
    filter_column: str,
    output_file: str,
):

    data_df = get_data_frame_from_file(data_file)
    filter_df = get_data_frame_from_file(filter_file)

    assert (
        from_column in filter_df.columns
    ), f"Column {from_column} not in {filter_file}"
    assert to_column in filter_df.columns, f"Column {to_column} not in {filter_file}"
    assert (
        filter_column in data_df.columns
    ), f"Column {filter_column} not in {data_file}"

    ranges = get_ranges(filter_df, from_column, to_column)
    filtered_df = filter_by_ranges(data_df, filter_column, ranges)

    filtered_df.sort_values(by=[filter_column], inplace=True)

    if ".xls" not in output_file:
        output_file += ".xlsx"

    filtered_df.to_excel(output_file, index=False)
