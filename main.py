"""
main.py — Entry Point
Thread Pool Management System - CSE316 CA2

Run this file to launch the application.
Usage:
    python main.py           → Launch GUI dashboard
    python main.py --bench   → Run benchmark only (no GUI)
"""

import sys


def run_gui():
    """Launch the GUI dashboard (Module 2)."""
    try:
        from gui_dashboard import main as gui_main
        print("Launching Thread Pool GUI Dashboard...")
        gui_main()
    except ImportError as e:
        print(f"GUI launch failed: {e}")
        print("Make sure tkinter is available (it ships with standard Python).")


def run_benchmark():
    """Run the performance benchmark (Module 3) without GUI."""
    from performance_analysis import run_benchmark_suite, print_bar_chart, plot_results
    results = run_benchmark_suite(
        task_counts=(10, 25, 50, 100),
        pool_size=4,
        task_duration=0.05,
    )
    print_bar_chart(results)
    plot_results(results)


if __name__ == "__main__":
    if "--bench" in sys.argv:
        run_benchmark()
    else:
        run_gui()
