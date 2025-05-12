import pandas as pd
import numpy as np
import itertools
import json
from collections import defaultdict

ORDER_SIZE = 5000
STEP = 100

class Venue:
    def __init__(self, ask, ask_size, fee=0.0, rebate=0.0):
        self.ask = ask
        self.ask_size = ask_size
        self.fee = fee
        self.rebate = rebate

def allocate(order_size, venues, λ_over, λ_under, θ_queue):
    N = len(venues)
    splits = [[]]
    for v in range(N):
        new_splits = []
        for alloc in splits:
            used = sum(alloc)
            max_v = min(order_size - used, venues[v].ask_size)
            for q in range(0, max_v + 1, STEP):
                new_splits.append(alloc + [q])
        splits = new_splits

    best_cost = float('inf')
    best_split = None
    for alloc in splits:
        if sum(alloc) != order_size:
            continue
        cost = compute_cost(alloc, venues, order_size, λ_over, λ_under, θ_queue)
        if cost < best_cost:
            best_cost = cost
            best_split = alloc
    return best_split, best_cost

def compute_cost(split, venues, order_size, λo, λu, θ):
    executed = 0
    cash_spent = 0
    for i in range(len(venues)):
        exe = min(split[i], venues[i].ask_size)
        executed += exe
        cash_spent += exe * (venues[i].ask + venues[i].fee)
        maker_rebate = max(split[i] - exe, 0) * venues[i].rebate
        cash_spent -= maker_rebate

    underfill = max(order_size - executed, 0)
    overfill = max(executed - order_size, 0)
    risk_pen = θ * (underfill + overfill)
    cost_pen = λu * underfill + λo * overfill
    return cash_spent + risk_pen + cost_pen

def preprocess_data(file_path='l1_day.csv'):
    df = pd.read_csv(file_path)
    df = df.sort_values('ts_event')
    df = df.groupby(['ts_event', 'publisher_id']).first().reset_index()
    return df

def get_snapshot(df, timestamp):
    snap = df[df['ts_event'] == timestamp]
    venues = []
    for _, row in snap.iterrows():
        if np.isnan(row['ask_px_00']) or np.isnan(row['ask_sz_00']):
            continue
        venues.append(Venue(row['ask_px_00'], int(row['ask_sz_00'])))
    return venues

def baseline_best_ask(df, order_size=ORDER_SIZE):
    filled = 0
    cash = 0
    for timestamp in df['ts_event'].unique():
        snap = df[df['ts_event'] == timestamp]
        best_row = snap.loc[snap['ask_px_00'].idxmin()] if not snap.empty else None
        if best_row is not None and best_row['ask_sz_00'] > 0:
            size = min(order_size - filled, best_row['ask_sz_00'])
            cash += size * best_row['ask_px_00']
            filled += size
        if filled >= order_size:
            break
    return cash, cash / filled if filled > 0 else None

def baseline_twap(df, order_size=ORDER_SIZE):
    timestamps = df['ts_event'].unique()
    chunk_size = int(order_size / len(timestamps)) + 1
    filled = 0
    cash = 0
    for timestamp in timestamps:
        snap = df[df['ts_event'] == timestamp]
        if snap.empty:
            continue
        ask_px = snap['ask_px_00'].mean()
        ask_sz = snap['ask_sz_00'].sum()
        size = min(chunk_size, order_size - filled, ask_sz)
        if np.isnan(ask_px) or ask_sz == 0:
            continue
        cash += size * ask_px
        filled += size
        if filled >= order_size:
            break
    return cash, cash / filled if filled > 0 else None

def baseline_vwap(df, order_size=ORDER_SIZE):
    df_valid = df.dropna(subset=['ask_px_00', 'ask_sz_00'])
    df_valid['dollar_volume'] = df_valid['ask_px_00'] * df_valid['ask_sz_00']
    total_volume = df_valid['ask_sz_00'].sum()
    if total_volume == 0:
        return None, None
    vwap_price = df_valid['dollar_volume'].sum() / total_volume
    return order_size * vwap_price, vwap_price

def run_backtest():
    df = preprocess_data()
    timestamps = df['ts_event'].unique()

    best_params = None
    best_cost = float('inf')
    best_fill_price = None
    total_cash_spent = None

    param_grid = list(itertools.product(
        [0.001, 0.01],      # λ_over
        [0.001, 0.01],      # λ_under
        [0.001, 0.01]       # θ_queue
    ))

    for λ_over, λ_under, θ_queue in param_grid:
        filled = 0
        cash = 0
        i = 0
        while filled < ORDER_SIZE and i < len(timestamps):
            venues = get_snapshot(df, timestamps[i])
            if not venues:
                i += 1
                continue
            split, _ = allocate(min(ORDER_SIZE - filled, ORDER_SIZE), venues, λ_over, λ_under, θ_queue)
            if split is None:
                i += 1
                continue
            for idx, venue in enumerate(venues):
                size = min(split[idx], venue.ask_size)
                cash += size * venue.ask
                filled += size
                if filled >= ORDER_SIZE:
                    break
            i += 1

        if filled >= ORDER_SIZE and cash < best_cost:
            best_cost = cash
            best_params = {
                'lambda_over': λ_over,
                'lambda_under': λ_under,
                'theta_queue': θ_queue
            }
            total_cash_spent = cash
            best_fill_price = cash / filled

    best_ask_cash, best_ask_avg = baseline_best_ask(df)
    twap_cash, twap_avg = baseline_twap(df)
    vwap_cash, vwap_avg = baseline_vwap(df)

    savings_vs_best_ask = ((best_ask_cash - total_cash_spent) / best_ask_cash) * 10000
    savings_vs_twap = ((twap_cash - total_cash_spent) / twap_cash) * 10000
    savings_vs_vwap = ((vwap_cash - total_cash_spent) / vwap_cash) * 10000

    output = {
        "best_params": best_params,
        "total_cash_spent": round(total_cash_spent, 2),
        "average_fill_price": round(best_fill_price, 4),
        "baseline_best_ask": {
            "total_cash_spent": round(best_ask_cash, 2),
            "average_fill_price": round(best_ask_avg, 4)
        },
        "baseline_twap": {
            "total_cash_spent": round(twap_cash, 2),
            "average_fill_price": round(twap_avg, 4)
        },
        "baseline_vwap": {
            "total_cash_spent": round(vwap_cash, 2),
            "average_fill_price": round(vwap_avg, 4)
        },
        "savings_vs_best_ask_bps": round(savings_vs_best_ask, 2),
        "savings_vs_twap_bps": round(savings_vs_twap, 2),
        "savings_vs_vwap_bps": round(savings_vs_vwap, 2)
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    run_backtest()
