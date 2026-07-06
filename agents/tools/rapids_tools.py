from typing import Literal

import pandas as pd


def aggregate_by_ward_category(df, backend: Literal["pandas", "cudf"] = "pandas"):
    if backend == "cudf":
        import cudf

        gdf = cudf.DataFrame.from_pandas(df)
        return gdf.groupby(["ward", "category"]).size().reset_index(name="complaint_count")
    return df.groupby(["ward", "category"]).size().reset_index(name="complaint_count")


def rolling_anomaly_scores(df, backend: Literal["pandas", "cudf"] = "pandas", window: int = 3):
    if backend == "cudf":
        import cudf

        gdf = cudf.DataFrame.from_pandas(df)
        gdf = gdf.sort_values(["ward", "category", "period"])
        gdf["rolling_avg"] = gdf.groupby(["ward", "category"])["complaint_count"].rolling(window).mean().reset_index(level=[0, 1], drop=True)
        gdf["anomaly_score"] = (gdf["complaint_count"] - gdf["rolling_avg"]) / (gdf["rolling_avg"] + 1)
        gdf["anomaly_flag"] = gdf["anomaly_score"] > 0.5
        return gdf

    df = df.sort_values(["ward", "category", "period"])
    df["rolling_avg"] = df.groupby(["ward", "category"])["complaint_count"].rolling(window).mean().reset_index(level=[0, 1], drop=True)
    df["anomaly_score"] = (df["complaint_count"] - df["rolling_avg"]) / (df["rolling_avg"] + 1)
    df["anomaly_flag"] = df["anomaly_score"] > 0.5
    return df
