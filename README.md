Here's a clean and professional `README.md` in English for your `vllm_benchmark_serving` GitHub directory:

---

# vllm\_benchmark\_serving

This repository provides a benchmarking framework to evaluate inference performance using the [vLLM](https://github.com/vllm-project/vllm) serving engine. It is based on the benchmarking utilities provided by the official [vLLM benchmarks](https://github.com/vllm-project/vllm/tree/main/benchmarks) directory.

## 📌 Purpose

The goal is to assess key performance metrics of vLLM's online serving capabilities, including:

* **Latency**
* **Throughput**
* **Time to First Token (TTFT)**

The benchmark assumes that the vLLM server is running in **OpenAI-compatible** mode. For setup instructions, please refer to the [vLLM Quickstart Guide](https://docs.vllm.ai/en/latest/getting_started/quickstart.html).

---

## 🔧 Setup

Install required Python packages using:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Edit the `combos.yaml` file to configure:

* `model`: the model name to benchmark
* `base_url`: URL of the running vLLM server
* `tokenizer`: the tokenizer to use for prompt tokenization

This tool benchmarks performance across different combinations of:

* `input_len`: input token length
* `output_len`: output token length
* `concurrency`: maximum number of concurrent requests
* `prompt`: number of prompts to be sent

---

## 🚀 Running Benchmarks

To start benchmarking based on your settings in `combos.yaml`:

```bash
python3 run_sweep.py
```

Results will be saved in the `results/` directory as individual `.json` files per test case.

---

## 📊 Aggregating Results

After all benchmarks have completed, run:

```bash
python3 aggregate_result.py
```

This will generate a single file `aggregate_results.csv` that summarizes all results.

---

## 📁 Output Structure

```
vllm_benchmark_serving/
├── backend_request_func.py
├── benchmark_serving.py
├── benchmark_dataset.py
├── combos.yaml
├── run_sweep.py
├── aggregate_result.py
├── requirements.txt
└── results/
    ├── run_1.json
    ├── run_2.json
    └── ...
```

---

## 📣 Notes

* Ensure the vLLM server is active and reachable at the specified `base_url` before starting the benchmarks.
* You can customize prompts, token lengths, and concurrency ranges in `combos.yaml`.

---

Let me know if you’d like to add example configs, charts, or results visualizations to the README as well!