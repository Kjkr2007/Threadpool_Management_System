"""
Module 1: Core Thread Pool Engine
Thread Pool Management System - CSE316 CA2
"""

import threading
import queue
import time
import logging
from typing import Callable, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)


class Task:
    """Represents a unit of work to be executed by the thread pool."""
    _id_counter = 0
    _lock = threading.Lock()

    def __init__(self, fn: Callable, args=(), kwargs=None, duration: float = 0):
        with Task._lock:
            Task._id_counter += 1
            self.task_id = Task._id_counter
        self.fn = fn
        self.args = args
        self.kwargs = kwargs or {}
        self.duration = duration  # simulated work duration in seconds
        self.submitted_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.result = None
        self.error = None

    @property
    def wait_time(self):
        if self.started_at:
            return self.started_at - self.submitted_at
        return None

    @property
    def exec_time(self):
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def __repr__(self):
        return f"Task(id={self.task_id}, duration={self.duration}s)"


class WorkerThread(threading.Thread):
    """A worker thread that pulls tasks from the shared queue and executes them."""

    def __init__(self, pool: 'ThreadPool', thread_id: int):
        super().__init__(name=f"Worker-{thread_id}", daemon=True)
        self.pool = pool
        self.thread_id = thread_id
        self.state = "idle"        # idle | running | terminated
        self.current_task: Optional[Task] = None
        self._stop_event = threading.Event()

    def run(self):
        logger.info(f"Worker-{self.thread_id} started.")
        while not self._stop_event.is_set():
            try:
                # Wait up to 0.5s for a task; loop to check stop event
                task = self.pool.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if task is None:  # Poison pill
                self.pool.task_queue.task_done()
                break

            self.state = "running"
            self.current_task = task
            task.started_at = time.time()

            with self.pool._stats_lock:
                self.pool.stats["tasks_started"] += 1

            logger.info(f"Worker-{self.thread_id} executing {task}")
            try:
                # Execute the actual function
                task.result = task.fn(*task.args, **task.kwargs)
                # Simulate additional work duration if specified
                if task.duration > 0:
                    time.sleep(task.duration)
            except Exception as e:
                task.error = e
                logger.error(f"Worker-{self.thread_id} error in {task}: {e}")

            task.completed_at = time.time()
            self.pool.task_queue.task_done()

            with self.pool._stats_lock:
                self.pool.stats["tasks_completed"] += 1
                self.pool.completed_tasks.append(task)

            logger.info(f"Worker-{self.thread_id} finished {task} in {task.exec_time:.3f}s")

            self.state = "idle"
            self.current_task = None

        self.state = "terminated"
        logger.info(f"Worker-{self.thread_id} terminated.")

    def stop(self):
        self._stop_event.set()


class ThreadPool:
    """
    Core Thread Pool Framework.
    Manages worker thread lifecycle, task queue, synchronization, and statistics.
    """

    def __init__(self, pool_size: int = 4, max_queue_size: int = 100):
        self.pool_size = pool_size
        self.max_queue_size = max_queue_size
        self.task_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.workers: list[WorkerThread] = []
        self.completed_tasks: list[Task] = []
        self._stats_lock = threading.Lock()
        self._pool_lock = threading.Lock()
        self._running = False
        self._thread_counter = 0

        self.stats = {
            "tasks_submitted": 0,
            "tasks_started": 0,
            "tasks_completed": 0,
        }

    def start(self):
        """Initialize and start all worker threads."""
        with self._pool_lock:
            if self._running:
                return
            self._running = True
            for _ in range(self.pool_size):
                self._spawn_worker()
        logger.info(f"ThreadPool started with {self.pool_size} workers.")

    def _spawn_worker(self):
        """Create and start a new worker thread."""
        self._thread_counter += 1
        worker = WorkerThread(self, self._thread_counter)
        self.workers.append(worker)
        worker.start()
        return worker

    def submit(self, fn: Callable, args=(), kwargs=None, duration: float = 0) -> Task:
        """Submit a task to the pool. Returns the Task object."""
        if not self._running:
            raise RuntimeError("ThreadPool is not running. Call start() first.")
        task = Task(fn, args, kwargs, duration)
        self.task_queue.put(task)
        with self._stats_lock:
            self.stats["tasks_submitted"] += 1
        logger.info(f"Submitted {task}")
        return task

    def resize(self, new_size: int):
        """Dynamically resize the thread pool."""
        with self._pool_lock:
            current = len([w for w in self.workers if w.state != "terminated"])
            if new_size > current:
                for _ in range(new_size - current):
                    self._spawn_worker()
                logger.info(f"Pool expanded to {new_size} workers.")
            elif new_size < current:
                to_remove = current - new_size
                for _ in range(to_remove):
                    self.task_queue.put(None)  # Poison pill for extra workers
                logger.info(f"Pool shrinking to {new_size} workers.")
            self.pool_size = new_size

    def shutdown(self, wait: bool = True):
        """Gracefully shutdown the pool. Finishes current tasks then terminates."""
        logger.info("Shutting down ThreadPool...")
        self._running = False
        active = [w for w in self.workers if w.state != "terminated"]
        for _ in active:
            self.task_queue.put(None)  # One poison pill per active worker
        if wait:
            for worker in self.workers:
                worker.join(timeout=10)
        logger.info("ThreadPool shutdown complete.")

    def get_status(self) -> dict:
        """Return current pool status snapshot."""
        thread_states = {}
        for w in self.workers:
            thread_states[w.name] = {
                "state": w.state,
                "task": str(w.current_task) if w.current_task else None
            }
        return {
            "pool_size": self.pool_size,
            "queue_size": self.task_queue.qsize(),
            "stats": dict(self.stats),
            "threads": thread_states
        }

    def get_performance_stats(self) -> dict:
        """Compute average wait/exec times from completed tasks."""
        if not self.completed_tasks:
            return {}
        wait_times = [t.wait_time for t in self.completed_tasks if t.wait_time is not None]
        exec_times = [t.exec_time for t in self.completed_tasks if t.exec_time is not None]
        return {
            "total_completed": len(self.completed_tasks),
            "avg_wait_time": round(sum(wait_times) / len(wait_times), 4) if wait_times else 0,
            "avg_exec_time": round(sum(exec_times) / len(exec_times), 4) if exec_times else 0,
            "min_exec_time": round(min(exec_times), 4) if exec_times else 0,
            "max_exec_time": round(max(exec_times), 4) if exec_times else 0,
        }


# ─── Demo / quick test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    def sample_task(task_num):
        time.sleep(0.1)
        return f"Task {task_num} done"

    pool = ThreadPool(pool_size=3)
    pool.start()

    for i in range(10):
        pool.submit(sample_task, args=(i,), duration=0.2)

    time.sleep(5)
    print(pool.get_performance_stats())
    pool.shutdown()
