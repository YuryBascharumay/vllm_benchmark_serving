import yaml
import subprocess
import os
import signal  # Необходимо для корректной остановки фонового процесса

# Path to benchmark_serving.py (relative path)
BENCHMARK_SCRIPT = "benchmark_serving.py"
# Load YAML config
CONFIG_FILE = "combos.yaml"


def run_benchmark(common_args, input_len, output_len, concurrency, num_prompts):
    """Run benchmark for a single combination of parameters."""
    args = common_args.copy()
    # Pass input/output token lengths
    args += ["--random-input-len", str(input_len), "--random-output-len", str(output_len)]
    # Set concurrency and num_prompts
    args += ["--max-concurrency", str(concurrency)]
    args += ["--num-prompts", str(num_prompts)]

    # Result directory
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)

    # 1. Формируем имена файлов для JSON (результат) и TXT (лог GPU)
    base_filename = f"bench_io{input_len}x{output_len}_mc{concurrency}_np{num_prompts}"
    json_outfile = os.path.join(result_dir, f"{base_filename}.json")
    gpu_log_file = os.path.join(result_dir, f"gpu_log_{base_filename}.txt")

    args += ["--save-result", "--result-filename", json_outfile]

    # 2. Подготавливаем команду мониторинга
    # Мы используем абсолютный путь для gpu_log_file, чтобы запись шла в правильную папку
    # sleep 10 можно уменьшить до sleep 1, если тесты проходят быстро
    monitor_cmd = f"while true; do date >> {gpu_log_file}; nvidia-smi >> {gpu_log_file}; sleep 10; done"

    print(f"Running: {' '.join(args)}")
    print(f"Logging GPU stats to: {gpu_log_file}")

    # 3. Запускаем мониторинг в фоне
    # preexec_fn=os.setsid создает новую группу процессов, чтобы мы могли убить 
    # весь shell-скрипт (включая sleep), а не только оболочку.
    monitor_process = subprocess.Popen(
        monitor_cmd,
        shell=True,
        executable="/bin/bash",
        preexec_fn=os.setsid
    )

    try:
        # 4. Запускаем основной бенчмарк
        ret = subprocess.run(args, capture_output=True, text=True)

        if ret.returncode != 0:
            print(f"Error for io=({input_len},{output_len}), mc={concurrency}, np={num_prompts}: {ret.stderr}")
        else:
            print(f"Finished io=({input_len},{output_len}), mc={concurrency}, np={num_prompts}, saved: {json_outfile}")

    finally:
        # 5. Останавливаем мониторинг (даже если бенчмарк упал с ошибкой)
        try:
            os.killpg(os.getpgid(monitor_process.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Could not kill monitor process: {e}")


def main():
    # Load settings from YAML
    with open(CONFIG_FILE, "r") as f:
        cfg = yaml.safe_load(f)
    model = cfg["model"]
    base_url = cfg["base_url"]
    tokenizer = cfg["tokenizer"]
    io_pairs = cfg.get("input_output", [])
    cp_pairs = cfg.get("concurrency_prompts", [])

    # Common arguments
    common_args = [
        "python3", BENCHMARK_SCRIPT,
        "--backend", "vllm",
        "--model", model,
        "--base-url", base_url,
        "--tokenizer", tokenizer,
        "--dataset-name", "random",
        "--percentile-metrics", "ttft,tpot,itl,e2el"
    ]

    # Cross-product execution
    for input_len, output_len in io_pairs:
        for concurrency, num_prompts in cp_pairs:
            run_benchmark(common_args, input_len, output_len, concurrency, num_prompts)


if __name__ == "__main__":
    main()