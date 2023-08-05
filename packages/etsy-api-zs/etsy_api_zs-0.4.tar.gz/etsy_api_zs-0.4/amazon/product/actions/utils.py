from io import StringIO

import pandas as pd
from ftfy import fix_encoding  # noqa: F401
from ftfy import fix_text


def excel_to_feed_string(
    file_path: str, sheet_name: str = "Template", encode: bool = True
):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    feed_string = df.to_csv(sep="\t", header=False, index=False)
    fixed_feed = fix_text(feed_string)
    if encode:
        fixed_feed = fixed_feed.encode("sloppy-windows-1252")
    return fixed_feed


def save_feed_string_to_tsv_file(feed_string: str, file_path: str):
    df = pd.read_csv(StringIO(feed_string["results"]), sep="\t")
    df.to_csv(file_path, sep="\t", index=None)
    return df
