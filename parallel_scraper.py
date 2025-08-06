# parallel_scraper.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from single_worker import scrape_group
import math

def run_multithread(chemicals, max_threads=3):
    chunk_size = math.ceil(len(chemicals) / max_threads)
    chunks = [chemicals[i:i + chunk_size] for i in range(0, len(chemicals), chunk_size)]

    results = []

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(scrape_group, chunk) for chunk in chunks]
        for future in as_completed(futures):
            try:
                result = future.result()
                results.extend(result)
            except Exception as e:
                print(f"❌ Thread failed: {e}")

    return results