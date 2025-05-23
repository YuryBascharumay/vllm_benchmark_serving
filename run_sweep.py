# Directory structure:
# experiments/
# ├── combos.yaml      # defines parameter combinations in YAML
# └── run_sweep.py     # driver script to execute benchmarks

# File: experiments/run_sweep.py
# Requires: pip install pyyaml
import yaml
import subprocess
import os

# Path to benchmark_serving.py (실제 위치로 상대 경로 지정)
BENCHMARK_SCRIPT = "benchmark_serving.py"
# Load YAML config
CONFIG_FILE = "combos.yaml"


def run_benchmark(common_args, input_len, output_len, concurrency, num_prompts):
    """Run benchmark for a single combination of parameters."""
    args = common_args.copy()
    # 입력/출력 토큰 수 전달
    args += ["--random-input-len", str(input_len), "--random-output-len", str(output_len)]
    # 동시성 및 num_prompts 설정
    args += ["--max-concurrency", str(concurrency)]
    args += ["--num-prompts", str(num_prompts)]

    # 결과 저장 디렉터리
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)
    outfile = os.path.join(
        result_dir,
        f"bench_io{input_len}x{output_len}_mc{concurrency}_np{num_prompts}.json"
    )
    args += ["--save-result", "--result-filename", outfile]

    print(f"Running: {' '.join(args)}")
    ret = subprocess.run(args, capture_output=True, text=True)
    if ret.returncode != 0:
        print(f"Error for io=({input_len},{output_len}), mc={concurrency}, np={num_prompts}: {ret.stderr}")
    else:
        print(f"Finished io=({input_len},{output_len}), mc={concurrency}, np={num_prompts}, saved: {outfile}")


def main():
    # YAML 파일에서 설정과 파라미터 목록 로드
    with open(CONFIG_FILE, "r") as f:
        cfg = yaml.safe_load(f)
    model = cfg["model"]
    base_url = cfg["base_url"]
    tokenizer = cfg["tokenizer"]
    io_pairs = cfg.get("input_output", [])
    cp_pairs = cfg.get("concurrency_prompts", [])

    # 공통 인자 구성
    common_args = [
        "python3", BENCHMARK_SCRIPT,
        "--backend", "vllm",
        "--model", model,
        "--base-url", base_url,
        "--tokenizer", tokenizer,
        "--dataset-name", "random",
    ]

    # 크로스-조합 실행 (각 io_pair마다 모든 concurrency-num_prompts 쌍)
    for input_len, output_len in io_pairs:
        for concurrency, num_prompts in cp_pairs:
            run_benchmark(common_args, input_len, output_len, concurrency, num_prompts)


if __name__ == "__main__":
    main()
