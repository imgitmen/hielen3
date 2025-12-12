import numpy as np
import pandas as pd
from hielen3 import db

def param_seek(row: pd.Series) -> pd.Series:
    """
    Input:  row -> Series con index = x (colonne del df originale), values = y
    Output: Series con a, b, r2, n per y = a*ln(x) + b
    """
    x = row.index.astype(float).to_numpy()
    y = row.to_numpy(dtype=float)

    m = (x > 0) & np.isfinite(y)
    n = int(m.sum())
    if n < 2:
        return pd.Series({"a": np.nan, "b": np.nan, "r2": np.nan, "n": n})

    X = np.log(x[m])
    Y = y[m]

    a, b = np.polyfit(X, Y, 1)

    Yhat = a * X + b
    ss_res = np.sum((Y - Yhat) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r2 = np.nan if ss_tot == 0 else 1 - ss_res / ss_tot

    return pd.Series({"a": a, "b": b, "r2": r2, "n": n})


def curve_build(params_row: pd.Series, x_dense: np.ndarray) -> pd.Series:
    """
    Input:  params_row -> Series con almeno 'a' e 'b'
            x_dense    -> array di x (tutti >0)
    Output: Series indicizzata da x_dense con y_hat = a*ln(x)+b
    """
    a = float(params_row["a"])
    b = float(params_row["b"])

    if not np.isfinite(a) or not np.isfinite(b):
        return pd.Series(np.nan, index=x_dense)

    y_hat = a * np.log(x_dense) + b
    return pd.Series(y_hat, index=x_dense)


def get_log_reg_frame(df):

    # definisci x_dense una volta (solo >0!)
    x_cols = df.columns.astype(float).to_numpy()
    x_pos = x_cols[x_cols > 0]
    x_dense = np.linspace(x_pos.min(), x_pos.max(), df.columns.__len__()*20)

    df_params = df.apply(param_seek, axis=1)  # -> colonne: a,b,r2,n
    df_curve  = df_params.apply(curve_build, axis=1, x_dense=x_dense)  # -> colonne: x_dense
    df_curve.columns = pd.Index(x_dense, name=None)
    return df_curve


def hielen_log_reg(sg_frame, sg_uuid):

    xx=db["series_groups"][sg_uuid]["label"].astype(float).reset_index("groupseries")["label"]
    sg_frame=sg_frame.T.join(xx).set_index("label").T
    sg_frame.index.name='timestamp'
    sg_frame.columns.name='x'

    return get_log_reg_frame(sg_frame)

