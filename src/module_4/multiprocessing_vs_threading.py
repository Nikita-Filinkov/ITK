import json
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from multiprocessing import Pool, Queue, Process
from queue import Empty
import time
from random import choices
from typing import List
from os import cpu_count


def numbers_info(count_number_in_result):
    def time_track(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            started_at = time.time()
            results = func(*args, **kwargs)
            ended_at = time.time()
            elapsed = round(ended_at - started_at, 4)
            data_to_save = {}
            for number, factorial in zip(data[:count_number_in_result], results):
                data_to_save.update({number: factorial})
            all_data_info[func.__name__] = {
                "execution_time": elapsed,
                "result": data_to_save,
            }
            return elapsed, results

        return wrapper

    return time_track


def generate_data(n: int) -> List[int]:
    return choices(range(1, 1001), k=n)


def process_number(number: int) -> int:
    factorial = 1
    for i in range(2, number + 1):
        factorial *= i
    return factorial


@numbers_info(10)
def one_thread():
    factorials = []
    for number in data:
        factorials.append(process_number(number))
    return factorials


@numbers_info(10)
def futures_threads():
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_number, data))
        return results


@numbers_info(10)
def pool_processes():
    max_workers = cpu_count()
    with Pool(processes=max_workers) as pool:
        results = list(pool.map(process_number, data))
    return results


def producer(number_queue: Queue, data: List[int], count_workers: int):
    for number in data:
        number_queue.put(number)
    for _ in range(count_workers):
        number_queue.put(None)


def consumer(number_queue: Queue, output_queue: Queue):
    while True:
        try:
            number = number_queue.get(timeout=1)
            if number is None:
                break
            result = process_number(number)
            output_queue.put(result)
        except Empty:
            break


@numbers_info(10)
def processes_with_queues():
    input_queue = Queue(maxsize=1000)
    results_queue = Queue()
    num_workers = cpu_count() - 1

    producer_in_queue = Process(target=producer, args=(input_queue, data, num_workers))
    producer_in_queue.start()

    processes = []
    for i in range(num_workers):
        handler_nums = Process(target=consumer, args=(input_queue, results_queue))
        processes.append(handler_nums)
        handler_nums.start()

    factorials = []

    while len(factorials) < len(data):
        try:
            num = results_queue.get(timeout=1)
            factorials.append(num)
        except Empty:
            break

    producer_in_queue.join()
    for process in processes:
        process.join()

    return factorials


def save_results_json(data_info):
    filename = "./factorials.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_info, f, indent=2, ensure_ascii=False)


def plot_comparison(filename: str = "performance_comparison.png"):
    methods = list(all_data_info.keys())
    times = [info["execution_time"] for info in all_data_info.values()]

    one_thread_idx = -1
    for i, method in enumerate(methods):
        if "one" in method.lower() or "одно" in method.lower():
            one_thread_idx = i
            break

    if one_thread_idx == -1:
        one_thread_idx = times.index(max(times))

    base_time_track = times[one_thread_idx]

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    bars = plt.bar(methods, times, color=["red", "blue", "green", "orange", "purple"])
    plt.title("Время выполнения методов")
    plt.xlabel("Метод")
    plt.ylabel("Время (сек)")
    plt.xticks(rotation=45, ha="right")

    for bar, time_val in zip(bars, times):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            f"{time_val:.2f}",
            ha="center",
            va="bottom",
        )

    plt.subplot(1, 2, 2)
    speedups = [base_time_track / t for t in times]

    bars2 = plt.bar(
        methods, speedups, color=["red", "blue", "green", "orange", "purple"]
    )
    plt.title("Ускорение относительно однопоточного варианта")
    plt.xlabel("Метод")
    plt.ylabel("Ускорение (раз)")
    plt.xticks(rotation=45, ha="right")

    for bar, speedup in zip(bars2, speedups):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            f"{speedup:.1f}x",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  График сохранен в {filename}")


if __name__ == "__main__":
    all_data_info = {}
    data = generate_data(100000)
    futures_threads_time, futures_threads_result = futures_threads()
    futures_processes_time, futures_processes_result = pool_processes()
    processes_with_queues_time, processes_with_queue_result = processes_with_queues()
    one_thread_time, one_thread_result = one_thread()
    save_results_json(all_data_info)
    plot_comparison(filename="./performance_comparison.png")

    print(f"Вариант 1 поток: {one_thread_time}")
    print(f"Вариант А: {futures_threads_time}")
    print(f"Вариант Б: {futures_processes_time}")
    print(f"Вариант B: {processes_with_queues_time}")
