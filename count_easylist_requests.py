import os
from typing import Set
import pandas as pd
import json
import statistics
from pathlib import Path
import yaml
import matplotlib.pyplot as plt
import matplotlib as mpl
from filelock import FileLock
from crawler import CrawlResults
from utils.utils import get_directories, get_domain, split
from utils.image_shingle import ImageShingle
import time
import numpy as np

CRAWL_NAME = "KJ2GW"

DATA_PATH = Path("/Users/siren/Code/IMC2024-CookielessBrowsing/cookie-classify/") / CRAWL_NAME
ANALYSIS_PATH = Path("analysis") / CRAWL_NAME
EASYLIST_PATH = Path("inputs") / "easylist" / "easylist.txt"

# Config
with open(DATA_PATH / "config.yaml", "r") as stream:
    config = yaml.safe_load(stream)

# Site list
site_list = []
with open(config["SITE_LIST_PATH"]) as file:
    for line in file:
        site_list.append(line.strip())

# Site queue
queue_lock = FileLock(config["QUEUE_PATH"] + ".lock", timeout=60)
with queue_lock:
    with open(config["QUEUE_PATH"], "r") as file:
        site_queue = json.load(file)

# Site results
results_lock = FileLock(config["RESULTS_PATH"] + ".lock", timeout=60)
with results_lock:
    with open(config["RESULTS_PATH"]) as file:
        site_results: dict[str, CrawlResults] = json.load(file)

"""
Check crawl completion.
"""
print(f"Crawled {len(site_results)}/{len(site_list)} sites.")

"""
Reduce the number of sites to analyze.
A successful site must have:
1. a successful domain -> url resolution
3. was not terminated via SIGKILL
2. no unexpected crawl exceptions
"""
successful_sites = []
unsuccessful_sites = []
keys: Set[str] = set()
for domain, result in site_results.items():
    keys.update(result.keys())
    if (
        result.get("url")
        and not result.get("SIGKILL")
        and not result.get("unexpected_exception")
    ):
        successful_sites.append(domain)
    else:
        unsuccessful_sites.append(domain)
print(f"{len(successful_sites)} successful sites.")

##############################################################################

import logging
from config import LOGGER_NAME

# Set up logging
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.DEBUG)
log_stream.setFormatter(formatter)
logger.addHandler(log_stream)


def get_trackers():
    """
    Get trackers from the EasyList.
    """
    trackers = set()
    with open(EASYLIST_PATH) as file:
        for line in file:
            trackers.add(line.strip())
    return trackers


def count_easylist_requests(sites: list, trackers) -> dict:
    """
    Extract differences for a list of sites.
    """
    res = {}
    for i, domain in enumerate(sites):
        logger.info(f"Analyzing {domain} ({i+1}/{len(sites)}).")

        # Take baseline har file from first clickstream
        har_path = Path(site_results[domain]["data_path"]) / "1" / "baseline.json"

        if har_path.is_file():
            with open(har_path) as data:
                try:
                    har = json.load(data)
                except json.JSONDecodeError:
                    logger.exception(f"Failed to read {har_path}.")

        res[domain] = 0
        entries = har["log"]["entries"]
        for entry in entries:
            if resquest := entry.get("request"):
                if url := resquest.get("url"):
                    if get_domain(url) in trackers:
                        res[domain] += 1

    return res


start_time = time.time()
trackers = get_trackers()
res = count_easylist_requests(successful_sites, trackers)
# Save the dictionary
with open(ANALYSIS_PATH / "easylist_requests.csv", "w") as f:
    df = pd.Series(res, name="easylist_requests")
    df.index.name = "domain"
    df.to_csv(f)
print(f"Completed in {time.time() - start_time} seconds.")
