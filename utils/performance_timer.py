# Modul: utils/performance_timer.py
import time

class PerformanceTimer:
    """
    Simple performance timer for measuring code execution duration.
    """

    def __init__(self):
        self.start_time = time.time()  # ✅ ihned při vytvoření začne měřit čas
        self.frame_count = 0

    def update(self):
        self.frame_count += 1

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()

    def stop(self):
        """Stop the timer and return elapsed time in seconds."""
        if self.start_time is None:
            raise RuntimeError("Timer was not started.")
        self.elapsed = time.perf_counter() - self.start_time
        return self.elapsed

    def reset(self):
        """Reset timer values."""
        self.start_time = None
        self.elapsed = 0.0

    def get_elapsed_ms(self):
        """Return elapsed time in milliseconds."""
        return self.elapsed * 1000.0

    def get_fps(self):
        """Vrátí průměrné FPS podle počtu snímků a uplynulého času."""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.frame_count / elapsed
