import re
import csv
import os
import sys
import argparse


def parse_nvidia_log_to_csv(input_file, output_file):
    """
    Парсит один файл лога nvidia-smi и сохраняет в csv.
    """
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

            print(
                f"[OK] {os.path.basename(input_file)} -> {os.path.basename(output_file)} ({len(rows_to_write)} строк)")
        else:
            print(f"[SKIP] В файле {os.path.basename(input_file)} не найдено данных.")

    except Exception as e:
        print(f"[ERROR] Ошибка при обработке {input_file}: {e}")


def process_directory(directory):
    """
    Сканирует папку на наличие .txt и запускает парсер для каждого.
    """
    if not os.path.exists(directory):
        print(f"[ERROR] Папка '{directory}' не существует.")
        return

    # Получаем список всех .txt файлов
    files = [f for f in os.listdir(directory) if f.endswith(".txt")]

    if not files:
        print(f"[INFO] В папке '{directory}' нет файлов с расширением .txt")
        return

    print(f"Обработка папки '{directory}'. Найдено файлов: {len(files)}")

    for filename in files:
        input_path = os.path.join(directory, filename)

        # Генерируем имя выходного файла (заменяем .txt на .csv)
        output_filename = os.path.splitext(filename)[0] + ".csv"
        output_path = os.path.join(directory, output_filename)

        parse_nvidia_log_to_csv(input_path, output_path)


def main():
    parser = argparse.ArgumentParser(description="Парсер логов nvidia-smi в CSV.")

    # Убрали required=True, теперь группа необязательна
    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument(
        '-i', '--input',
        type=str,
        help='Путь к одному файлу лога (.txt)'
    )

    group.add_argument(
        '-d', '--dir',
        type=str,
        help='Путь к папке (по умолчанию: results)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Путь к выходному CSV (только для режима -i)'
    )

    args = parser.parse_args()

    # ЛОГИКА ВЫБОРА РЕЖИМА

    # 1. Если указан конкретный файл (-i)
    if args.input:
        if not os.path.exists(args.input):
            print(f"[ERROR] Файл '{args.input}' не существует.")
            sys.exit(1)

        if args.output:
            output_filename = args.output
        else:
            base_name, _ = os.path.splitext(args.input)
            output_filename = base_name + ".csv"

        parse_nvidia_log_to_csv(args.input, output_filename)

    # 2. Если указана конкретная папка (-d)
    elif args.dir:
        process_directory(args.dir)

    # 3. ПО УМОЛЧАНИЮ (если ничего не указано) -> папка results
    else:
        default_dir = "results"
        print(f"[INFO] Аргументы не указаны. Ищем логи в папке '{default_dir}'...")
        process_directory(default_dir)


if __name__ == "__main__":
    main()