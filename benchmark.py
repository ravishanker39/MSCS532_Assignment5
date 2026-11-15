"""Measure both pivot rules on paired inputs, then count comparisons separately."""

import argparse
import csv
import json
import platform
import random
import statistics
import time
from pathlib import Path

from quicksort import deterministic_quicksort, randomized_quicksort

SIZES = (256, 512, 1024, 2048, 4096)
SHAPES = ("random", "ascending", "descending", "eight_keys", "all_equal")
POLICIES = ("last", "random")
TRIALS = 7
SEED = 53205


def make_input(size, shape, seed):
    rng = random.Random(seed)
    if shape == "eight_keys":
        return [rng.randrange(8) for _ in range(size)]
    if shape == "all_equal":
        return [7] * size
    values = list(range(size))
    if shape == "random":
        rng.shuffle(values)
    elif shape == "descending":
        values.reverse()
    return values


def run_sort(policy, values, rng):
    if policy == "last":
        deterministic_quicksort(values)
    else:
        randomized_quicksort(values, rng)


class CountedKey:
    """Count only comparisons made inside the sorting routine."""

    comparisons = 0

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        CountedKey.comparisons += 1
        return self.value < other.value


def count_keys(policy, data, pivot_seed):
    wrapped = [CountedKey(value) for value in data]
    CountedKey.comparisons = 0
    run_sort(policy, wrapped, random.Random(pivot_seed))
    if [key.value for key in wrapped] != sorted(data):
        raise AssertionError("counted run did not sort the input")
    return CountedKey.comparisons


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("benchmark_run"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    # Give each pivot policy one untimed sort before collecting its timings.
    for policy in POLICIES:
        data = make_input(256, "random", SEED)
        run_sort(policy, data, random.Random(SEED))

    rows, summaries = [], []
    for size in SIZES:
        for index, shape in enumerate(SHAPES):
            elapsed = {policy: [] for policy in POLICIES}
            first_seed = SEED + size * 1000 + index * 20
            for trial in range(TRIALS):
                data_seed = first_seed + trial
                pivot_seed = data_seed + 1_000_000
                data = make_input(size, shape, data_seed)
                expected = sorted(data)
                # Alternate which policy runs first across successive trials.
                order = POLICIES if (trial + index) % 2 == 0 else POLICIES[::-1]
                for policy in order:
                    # Each sort changes its input. A fresh copy gives both
                    # policies the same starting order, including on shuffled data.
                    values = data.copy()
                    rng = random.Random(pivot_seed)
                    # Time just the sort. Check the result after stopping the clock.
                    start = time.perf_counter_ns()
                    run_sort(policy, values, rng)
                    duration = time.perf_counter_ns() - start
                    if values != expected:
                        raise AssertionError((shape, size, policy, trial))
                    elapsed[policy].append(duration)
                    rows.append(dict(size=size, shape=shape, trial=trial + 1,
                                     pivot=policy, data_seed=data_seed,
                                     pivot_seed=pivot_seed if policy == "random" else "",
                                     elapsed_ns=duration))
            for policy in POLICIES:
                times = elapsed[policy]
                summaries.append(dict(size=size, shape=shape, pivot=policy,
                                      median_ms=statistics.median(times) / 1e6,
                                      min_ms=min(times) / 1e6, max_ms=max(times) / 1e6,
                                      first_trial_key_comparisons=0))
    # Replay trial 1 with the same data and pivot seeds. Counting comparisons
    # separately keeps the counter updates out of the measured sort times.
    for row in summaries:
        first_seed = SEED + row["size"] * 1000 + SHAPES.index(row["shape"]) * 20
        data = make_input(row["size"], row["shape"], first_seed)
        row["first_trial_key_comparisons"] = count_keys(row["pivot"], data, first_seed + 1_000_000)

    write_csv(args.output / "trials.csv", rows)
    write_csv(args.output / "summary.csv", summaries)
    cpu = platform.processor() or platform.machine()
    cpu_info = Path("/proc/cpuinfo")
    if cpu_info.is_file():
        for line in cpu_info.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.partition(":")[2].strip()
                break
    environment = dict(python=platform.python_version(), implementation=platform.python_implementation(),
                       system=platform.system(), architecture=platform.machine(), cpu=cpu,
                       clock="perf_counter_ns", trials_per_cell=TRIALS, base_seed=SEED)
    (args.output / "environment.json").write_text(
        json.dumps(environment, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Verified {len(rows)} timed sorts and {len(summaries)} comparison-count runs.")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
