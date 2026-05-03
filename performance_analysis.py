"""
Module 3: Performance Analysis & Benchmarking
Thread Pool Management System - CSE316 CA2

Compares Thread Pool vs Thread-per-Task approach.
Generates charts and exports a CSV log.
"""

import threading
import time
import csv
import os
import statistics
from thread_pool import ThreadPool


# ─── Simulated workload ─────────────────────────────────────────────────────

def cpu_task(n: int, duration: float = 0.1):
    """Simulates a short CPU-bound task."""
    result = 0
    deadline = time.time() + duration
    while time.time() < deadline:
        result += n * n
    return result


# ─── Benchmark: Thread Pool ──────────────────────────────────────────────────

def benchmark_thread_pool(num_tasks: int, pool_size: int = 4,
                           task_duration: float = 0.1) -> dict:
    """Run num_tasks using a thread pool and return timing stats."""
    pool = ThreadPool(pool_size=pool_size)
    pool.start()

    start = time.perf_counter()
    for i in range(num_tasks):
        pool.submit(cpu_task, args=(i, task_duration))

    pool.task_queue.join()          # Wait for all tasks to finish
    elapsed = time.perf_counter() - start

    perf = pool.get_performance_stats()
    pool.shutdown(wait=False)

    return {
        "approach": "Thread Pool",
        "num_tasks": num_tasks,
        "pool_size": pool_size,
        "total_time": round(elapsed, 4),
        "avg_exec_time": perf.get("avg_exec_time", 0),
        "avg_wait_time": perf.get("avg_wait_time", 0),
        "throughput": round(num_tasks / elapsed, 2),
    }


# ─── Benchmark: Thread-per-Task ──────────────────────────────────────────────

def benchmark_thread_per_task(num_tasks: int, task_duration: float = 0.1) -> dict:
    """Spawn a new thread for every task and measure total time."""
    threads = []
    start = time.perf_counter()

    for i in range(num_tasks):
        t = threading.Thread(target=cpu_task, args=(i, task_duration), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start

    return {
        "approach": "Thread-per-Task",
        "num_tasks": num_tasks,
        "pool_size": num_tasks,           # one thread per task
        "total_time": round(elapsed, 4),
        "avg_exec_time": round(task_duration, 4),
        "avg_wait_time": 0.0,
        "throughput": round(num_tasks / elapsed, 2),
    }


# ─── Full Benchmark Suite ────────────────────────────────────────────────────

def run_benchmark_suite(task_counts=(10, 25, 50, 100),
                        pool_size: int = 4,
                        task_duration: float = 0.1,
                        csv_path: str = "benchmark_results.csv") -> list[dict]:
    """
    Run both approaches for multiple task counts.
    Returns list of result dicts and saves CSV.
    """
    results = []
    print(f"\n{'='*60}")
    print(f"  THREAD POOL BENCHMARK SUITE")
    print(f"  Pool Size: {pool_size} | Task Duration: {task_duration}s")
    print(f"{'='*60}")
    print(f"{'Tasks':>8} | {'Approach':<20} | {'Time(s)':>8} | {'Throughput':>12}")
    print(f"{'-'*60}")

    for n in task_counts:
        # Thread Pool
        r1 = benchmark_thread_pool(n, pool_size=pool_size, task_duration=task_duration)
        results.append(r1)
        print(f"{n:>8} | {'Thread Pool':<20} | {r1['total_time']:>8.3f} | {r1['throughput']:>10.1f}/s")

        # Thread-per-Task
        r2 = benchmark_thread_per_task(n, task_duration=task_duration)
        results.append(r2)
        print(f"{n:>8} | {'Thread-per-Task':<20} | {r2['total_time']:>8.3f} | {r2['throughput']:>10.1f}/s")
        print(f"{'-'*60}")

    # Save to CSV
    if results:
        keys = results[0].keys()
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nResults saved to: {csv_path}")

    return results


# ─── Text-based chart ────────────────────────────────────────────────────────

def print_bar_chart(results: list[dict]):
    """Print a simple ASCII bar chart of total_time by approach and task count."""
    print(f"\n{'='*60}")
    print("  PERFORMANCE CHART — Total Time (s) — lower is better")
    print(f"{'='*60}")

    pool_results = [r for r in results if r["approach"] == "Thread Pool"]
    tpt_results  = [r for r in results if r["approach"] == "Thread-per-Task"]

    max_time = max(r["total_time"] for r in results) if results else 1
    bar_width = 40

    for p, t in zip(pool_results, tpt_results):
        n = p["num_tasks"]
        print(f"\n  Tasks = {n}")
        pb = int((p["total_time"] / max_time) * bar_width)
        tb = int((t["total_time"] / max_time) * bar_width)
        print(f"  Pool  [{('█' * pb):<{bar_width}}] {p['total_time']:.3f}s")
        print(f"  T/T   [{('█' * tb):<{bar_width}}] {t['total_time']:.3f}s")

    print(f"\n{'='*60}")


# ─── Matplotlib chart (optional) ─────────────────────────────────────────────

def plot_results(results: list[dict], save_path: str = "benchmark_chart.png"):
    """Generate a matplotlib bar chart. Falls back gracefully if not installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        pool_r = [r for r in results if r["approach"] == "Thread Pool"]
        tpt_r  = [r for r in results if r["approach"] == "Thread-per-Task"]

        x = np.arange(len(pool_r))
        width = 0.35
        labels = [str(r["num_tasks"]) + " tasks" for r in pool_r]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Thread Pool vs Thread-per-Task — Performance Comparison",
                     fontsize=13, fontweight="bold")

        # Total time
        ax1.bar(x - width/2, [r["total_time"] for r in pool_r],
                width, label="Thread Pool", color="#7C83FD")
        ax1.bar(x + width/2, [r["total_time"] for r in tpt_r],
                width, label="Thread-per-Task", color="#F44336", alpha=0.8)
        ax1.set_xlabel("Number of Tasks")
        ax1.set_ylabel("Total Time (s)")
        ax1.set_title("Total Execution Time")
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels)
        ax1.legend()
        ax1.grid(axis="y", alpha=0.3)

        # Throughput
        ax2.bar(x - width/2, [r["throughput"] for r in pool_r],
                width, label="Thread Pool", color="#4CAF50")
        ax2.bar(x + width/2, [r["throughput"] for r in tpt_r],
                width, label="Thread-per-Task", color="#FFC107", alpha=0.8)
        ax2.set_xlabel("Number of Tasks")
        ax2.set_ylabel("Tasks per Second")
        ax2.set_title("Throughput Comparison")
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)
        ax2.legend()
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"Chart saved to: {save_path}")
        return save_path

    except ImportError:
        print("matplotlib not installed — skipping chart generation.")
        return None


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_benchmark_suite(
        task_counts=(10, 25, 50, 100),
        pool_size=4,
        task_duration=0.05,
        csv_path="benchmark_results.csv"
    )
    print_bar_chart(results)
    plot_results(results, save_path="benchmark_chart.png")
