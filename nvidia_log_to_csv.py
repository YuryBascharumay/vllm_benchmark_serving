import re
import csv
import os
import sys
import argparse


def parse_nvidia_log_to_csv(input_file, output_file):
    # Регулярные выражения
    date_pattern = re.compile(r"^(\w{3}\s+\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\S*\s?\d{4})")
    gpu_id_pattern = re.compile(r"\|\s+(\d+)\s+NVIDIA")

    # Метрики: Power, Memory, Util
    metrics_pattern = re.compile(
        r"\|\s+\d+%\s+\d+C\s+\S+\s+"
        r"(?P<pwr_use>\d+)W\s+/\s+(?P<pwr_cap>\d+)W"
        r"\s+\|\s+"
        r"(?P<mem_use>\d+)MiB\s+/\s+(?P<mem_tot>\d+)MiB"
        r"\s+\|\s+"
        r"(?P<util>\d+)%"
    )

    rows_to_write = []
    current_date = None
    current_gpu_id = None

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Поиск даты
                date_match = date_pattern.search(line)
                if date_match:
                    current_date = date_match.group(1)
                    continue

                # Поиск GPU ID
                gpu_match = gpu_id_pattern.search(line)
                if gpu_match:
                    current_gpu_id = gpu_match.group(1)
                    continue

                # Поиск метрик
                metrics_match = metrics_pattern.search(line)
                if metrics_match and current_date and current_gpu_id is not None:
                    m = metrics_match.groupdict()

                    rows_to_write.append({
                        'timestamp': current_date,
                        'gpu_id': current_gpu_id,
                        'pwr_usage_w': m['pwr_use'],
                        'pwr_cap_w': m['pwr_cap'],
                        'mem_usage_mib': m['mem_use'],
                        'mem_total_mib': m['mem_tot'],
                        'gpu_util_pct': m['util']
                    })
                    current_gpu_id = None

        # Запись результата
        if rows_to_write:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'gpu_id',
                    'pwr_usage_w', 'pwr_cap_w',
                    'mem_usage_mib', 'mem_total_mib',
                    'gpu_util_pct'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows_to_write)

            print(f"[OK] Обработано записей: {len(rows_to_write)}")
            print(f"[OK] Результат сохранен в: {output_file}")
        else:
            print("[INFO] В файле не найдено данных для парсинга.")

    except Exception as e:
        print(f"[ERROR] Ошибка при обработке: {e}")


def main():
    parser = argparse.ArgumentParser(description="Парсер логов nvidia-smi в CSV.")

    parser.add_argument(
        '-i', '--input',
        type=str,
        default='gpu_log.txt',
        help='Путь к входному файлу лога'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        required=False,
        help='Путь к выходному CSV файлу (по умолчанию: рядом с исходным)'
    )

    args = parser.parse_args()
    input_filename = args.input

    if not os.path.exists(input_filename):
        print(f"[ERROR] Файл '{input_filename}' не существует.")
        sys.exit(1)

    if args.output:
        output_filename = args.output
    else:
        base_name, _ = os.path.splitext(input_filename)
        output_filename = base_name + ".csv"

    print(f"Чтение файла: {input_filename}")
    parse_nvidia_log_to_csv(input_filename, output_filename)


if __name__ == "__main__":
    main()