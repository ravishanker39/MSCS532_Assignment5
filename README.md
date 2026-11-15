# Assignment 5 · Deterministic and randomized Quicksort

Ravi Shanker Thadishetti · MSCS-532-B01 · University of the Cumberlands

How much does input order matter when the only algorithmic difference is the pivot rule? This Python implementation compares the last key with a uniformly sampled key from the current subarray. Both versions partition in place, remove the entire group tied with the pivot, and recurse on the smaller side.

## Run

Use Python 3.10 or later. All commands run from the repository root and use the standard library.

```sh
python quicksort.py --pivot last 4 1 3 2 5 3
python quicksort.py --pivot random --seed 42 4 1 3 2 5 3
python -m unittest -v
python benchmark.py
```

Both examples print `[1, 2, 3, 3, 4, 5]`. From Python, call `deterministic_quicksort(values)` or `randomized_quicksort(values, rng)`. Each modifies the list and returns `None`. Supply a `random.Random` instance to replay pivot choices, or omit it to use a fresh generator. The list must contain mutually comparable values with a consistent order. Equal records may change relative order.

## Findings

On 4,096 ascending keys, the last pivot took **577.630 ms**, compared with **4.478 ms** for the random pivot (medians of seven runs). On shuffled distinct keys of the same size the last pivot was faster, **4.432 ms** versus **5.056 ms**. With identical keys both methods completed one partition and made exactly **8,190 key comparisons**. The results show why the input order and the number of distinct keys matter when choosing a pivot policy.

## Files and results

- [Written report](report/Assignment5_Ravi_Shanker_Thadishetti.docx) — design, partition trace, time and space derivations, experiments, and interpretation.
- [Implementation](quicksort.py) and [correctness tests](test_quicksort.py).
- [Benchmark](benchmark.py) — five input sizes, five distributions and seven paired trials per condition. Input construction, copying, validation and generator setup are outside the timed interval. Key comparisons are counted in separate replays of trial 1.
- [Raw timings](results/trials.csv), [median, range and comparison counts](results/summary.csv), and [execution environment](results/environment.json).

Running the benchmark creates a new `benchmark_run/` directory for local measurements. Seeds reproduce the inputs and pivot choices. Elapsed times depend on the machine and its load.
