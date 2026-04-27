import time
import threading
from scanner import check_signal


class RadarEngine:
    def __init__(self, tickers):
        self.tickers = tickers
        self.cache = []
        self.last_scan = 0
        self.refresh_rate = 10
        self.lock = threading.Lock()
        self.running = False

    # -----------------------------
    # SINGLE SCAN CYCLE
    # -----------------------------
    def scan(self):
        results = []

        for t in self.tickers:
            try:
                res = check_signal(t)
                if res:
                    results.append(res)
            except:
                pass

        results.sort(key=lambda x: x["score"], reverse=True)

        with self.lock:
            self.cache = results
            self.last_scan = time.time()

    # -----------------------------
    # BACKGROUND LOOP (INSTITUTIONAL STYLE)
    # -----------------------------
    def start(self, refresh_rate):
        self.refresh_rate = refresh_rate
        self.running = True

        def loop():
            while self.running:
                self.scan()
                time.sleep(self.refresh_rate)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()

    # -----------------------------
    # SAFE READ ACCESS
    # -----------------------------
    def get_data(self):
        with self.lock:
            return self.cache

    def stop(self):
        self.running = False
