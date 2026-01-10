#!/bin/bash
# Benchmark runner for api-governance-skill

set -e

echo "=== API Governance Benchmarks ==="
echo ""

# Check if installed
if ! command -v api-governor &> /dev/null; then
    echo "Error: api-governor not installed. Run: pip install -e ."
    exit 1
fi

# Create test specs if they don't exist
if [ ! -f "specs/small.yaml" ]; then
    echo "Generating test specs..."
    python generate_test_specs.py
fi

echo "Running benchmarks..."
echo ""

# Parse benchmarks
echo "=== Parse Benchmarks ==="
for size in small medium large; do
    echo -n "$size: "
    time api-governor specs/$size.yaml --json > /dev/null 2>&1
done

echo ""
echo "=== Diff Benchmarks ==="
for size in small medium large; do
    echo -n "$size: "
    time api-governor specs/${size}_v2.yaml --baseline specs/${size}_v1.yaml --json > /dev/null 2>&1
done

echo ""
echo "=== Memory Benchmarks ==="
# Requires: pip install memory-profiler
if command -v mprof &> /dev/null; then
    for size in small medium large; do
        echo "$size:"
        mprof run api-governor specs/$size.yaml --json > /dev/null 2>&1
        mprof peak
        rm -f mprofile_*.dat
    done
else
    echo "Install memory-profiler for memory benchmarks: pip install memory-profiler"
fi

echo ""
echo "Done."
