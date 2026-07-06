import time
import pandas as pd
from data.generate_synthetic_data import write_csv, generate_complaint
from agents.tools.rapids_tools import aggregate_by_ward_category, rolling_anomaly_scores


def build_dataframe(rows):
    return pd.DataFrame(rows)


def benchmark(rows):
    df = build_dataframe(rows)
    results = {}
    for backend in ["pandas"]:
        start = time.time()
        agg = aggregate_by_ward_category(df, backend=backend)
        anomalies = rolling_anomaly_scores(agg, backend=backend)
        results[backend] = time.time() - start
    print(results)
    return results


if __name__ == "__main__":
    rows = [generate_complaint(i) for i in range(200000)]
    results = benchmark(rows)
    print(f"Benchmark results: {results}")
