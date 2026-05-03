Thread Pool Management System

Thread Pool Management System is a concurrent application designed to efficiently manage multiple tasks using a fixed number of worker threads. The system demonstrates thread creation, reuse, synchronization, and graceful termination, reducing overhead compared to traditional thread-per-task execution. It includes a real-time visual simulator and performance analysis to showcase improved throughput and scalability in multithreaded environments.

🚀 Features
Thread pool initialization with configurable size
Task submission (single & batch)
Thread reuse (no unnecessary thread creation)
Real-time thread state visualization (Idle / Running / Terminated)
Queue management system
Performance comparison (Thread Pool vs Thread-per-Task)
Graceful shutdown mechanism
🖥️ Project Structure
.
├── thread_pool.py          # Core thread pool logic
├── gui_dashboard.py        # Tkinter GUI dashboard
├── main.py                 # Entry point
├── performance_analysis.py # Benchmark module
├── index_2.html            # Web-based simulator
▶️ How to Run
🔹 Option 1: HTML Simulator (Easiest)
open index_2.html

OR double-click the file

👉 Runs directly in browser (no setup required)

🔹 Option 2: Python GUI
python3 main.py

If warning appears:

export TK_SILENCE_DEPRECATION=1
python3 main.py
🔹 Option 3: Benchmark Mode
python3 main.py --bench
🎮 How to Use
HTML Simulator
Click ▶ Start Pool
Click + Task or + Batch
Watch threads execute tasks in real time
Python GUI
Start pool
Submit tasks
Monitor thread activity
🧠 Concepts Covered
Thread creation and reuse
Synchronization using queues
Producer-consumer model
Concurrent execution
Performance optimization
🛠️ Technologies Used
Python (threading, queue, tkinter)
HTML, CSS, JavaScript
Matplotlib (for benchmarking)
📊 Benchmark

The system compares:

Thread Pool
Thread-per-Task

Metrics:

Execution time
Throughput
📌 Project Objective

To design a system that efficiently manages threads, reduces overhead, and improves performance in concurrent applications.

🔮 Future Scope
Web-based backend integration
Cloud deployment
Advanced scheduling algorithms
Real-time analytics dashboard
👨‍💻 Author

K Jaswanth Kumar Reddy
B.Tech CSE (Cloud Computing)

📎 Note
HTML version is a simulation
Python version provides actual thread execution
