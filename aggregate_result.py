# File: experiments/aggregate_results.py
# Requires: pip install pandas

import glob
import json
import pandas as pd
import os

RESULT_DIR = "results"
OUT_CSV = os.path.join(RESULT_DIR, "aggregate_results.csv")

def main():
    # 1) results/*.json 파일 목록
    json_paths = glob.glob(os.path.join(RESULT_DIR, "*.json"))
    if not json_paths:
        print("No JSON files found in results/.")
        return

    # 2) 각 JSON을 읽어서 리스트에 담기
    records = []
    for p in json_paths:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            records.append(data)

    # 3) pandas DataFrame 생성 및 CSV로 출력
    df = pd.json_normalize(records)
    df.to_csv(OUT_CSV, index=False)
    print(f"Aggregated {len(records)} runs → {OUT_CSV}")

if __name__ == "__main__":
    main()
