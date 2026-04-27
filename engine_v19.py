import time
import threading
from universe import discover_movers
from scanner import check_signal


class AutonomousScanner:

    def __init__(self):
        self.data = []
        self.last_run = 0
        self.running = False
        self.lock = threading.Lock()

    # -----------------------------
    # FULL SCAN PIPELINE
    # -----------------------------
    def scan(self):

        tickers = discover_movers()

        results = []

        for t in tickers:
            try:
                res = check_signal(t)
                if res and res["score"] > 40:  # filter noise
                    results.append(res)
            except:
                pass

        results.sort(key=lambda x: x["score"], reverse=True)

        with self.lock:
            self.data = results
            self.last_run = time.time()

    # -----------------------------
    # BACKGROUND LOOP
    # -----------------------------
    def start(self, interval=10):

        self.running = True

        def loop():
            while self.running:
                self.scan()
                time.sleep(interval)

        threading.Thread(target=loop, daemon=True).start()

    # -----------------------------
    # SAFE READ
    # -----------------------------
    def get(self):
        with self.lock:
            return self.data

    def stop(self):
        self.running = False
