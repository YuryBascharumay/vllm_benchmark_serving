# File: experiments/aggregate_results.py
# Requires: pip install pandas

import glob
import json
import pandas as pd
import os
import re

RESULT_DIR = "results"
OUT_CSV = os.path.join(RESULT_DIR, "aggregate_results.csv")

def parse_input_output_lengths(filename):
    """bench_io256x256_mc32_np128.json → input_len=256, output_len=256"""
    match = re.search(r"io(\d+)x(\d+)", filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def main():
    # 1) results/*.json 파일 목록
    json_paths = glob.glob(os.path.join(RESULT_DIR, "*.json"))
    if not json_paths:
        print("No JSON files found in results/.")
        return

    # 2) 각 JSON을 읽어서 리스트에 담기 + input/output 길이 추가
    records = []
    for p in json_paths:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        filename = os.path.basename(p)
        input_len, output_len = parse_input_output_lengths(filename)
        data["input_len"] = input_len
        data["output_len"] = output_len
        data["filename"] = filename

        records.append(data)

    # 3) pandas DataFrame 생성 및 CSV로 출력
    df = pd.json_normalize(records)
    df.to_csv(OUT_CSV, index=False)
    print(f"Aggregated {len(records)} runs → {OUT_CSV}")

if __name__ == "__main__":
    main()
