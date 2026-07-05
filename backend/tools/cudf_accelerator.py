"""
Analytics accelerator – uses NVIDIA RAPIDS cuDF if available,
otherwise falls back to pandas & scikit-learn for CPU-only environments.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Try to import GPU libraries; if not present, fall back to CPU
try:
    import cudf
    from cuml.cluster import DBSCAN
    HAS_GPU = True
except ImportError:
    cudf = None
    DBSCAN = None
    HAS_GPU = False

def load_complaints_to_gpu(complaints: List[Dict[str, Any]]):
    """Convert a list of complaint dicts to a DataFrame (GPU or CPU)."""
    if HAS_GPU:
        df = cudf.DataFrame(complaints)
        if 'timestamp' in df.columns:
            df['timestamp'] = cudf.to_datetime(df['timestamp'])
        return df
    else:
        df = pd.DataFrame(complaints)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

def compute_ward_category_counts(df):
    """Compute complaints per (ward, category)."""
    if HAS_GPU:
        pivot = df.groupby(['location_ward', 'category']).size().reset_index(name='count')
        return pivot
    else:
        pivot = df.groupby(['location_ward', 'category']).size().reset_index(name='count')
        return pivot

def detect_severity_spikes(df, time_col='timestamp', severity_col='severity',
                           freq='D', threshold=2.0):
    """Detect days where high/critical complaints exceed rolling average * threshold."""
    if HAS_GPU:
        mask = df[severity_col].isin(['high', 'critical'])
        high_sev = df[mask].copy()
        if high_sev.empty:
            return cudf.DataFrame()
        daily = high_sev.groupby(cudf.Grouper(key=time_col, freq=freq)).size().reset_index(name='count')
        daily['rolling_avg'] = daily['count'].rolling(window=7, min_periods=1).mean()
        daily['spike'] = daily['count'] > (daily['rolling_avg'] * threshold)
        return daily[daily['spike']][['timestamp', 'count']]
    else:
        mask = df[severity_col].isin(['high', 'critical'])
        high_sev = df[mask].copy()
        if high_sev.empty:
            return pd.DataFrame()
        daily = high_sev.set_index(time_col).resample(freq).size().reset_index(name='count')
        daily['rolling_avg'] = daily['count'].rolling(window=7, min_periods=1).mean()
        daily['spike'] = daily['count'] > (daily['rolling_avg'] * threshold)
        return daily[daily['spike']][['timestamp', 'count']]

def compute_location_clusters(df, lat_col='latitude', lon_col='longitude',
                              eps=0.001, min_samples=3):
    """
    GPU-accelerated DBSCAN clustering if GPU available, else CPU DBSCAN from sklearn.
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        return df.assign(cluster=-1)
    
    coords = df[[lat_col, lon_col]].dropna().astype('float32')
    if len(coords) < min_samples:
        return df.assign(cluster=-1)
    
    if HAS_GPU:
        db = DBSCAN(eps=eps, min_samples=min_samples)
        df['cluster'] = db.fit_predict(coords)
    else:
        from sklearn.cluster import DBSCAN as CPUDBSCAN
        db = CPUDBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
        df['cluster'] = db.fit_predict(coords)
    return df