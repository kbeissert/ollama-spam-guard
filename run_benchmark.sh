#!/bin/bash
./.venv/bin/python scripts/benchmark/spam_benchmark.py --model qwen3:8b > benchmark_output.txt 2>&1
