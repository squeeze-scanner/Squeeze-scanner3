from concurrent.futures import ThreadPoolExecutor
from scanner import check_signal
from universe import UNIVERSE


def scan_all():
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_signal, t) for t in UNIVERSE]

        for f in futures:
            try:
                res = f.result()
                if res:
                    results.append(res)
            except:
                pass

    return sorted(results, key=lambda x: x["score"], reverse=True)
