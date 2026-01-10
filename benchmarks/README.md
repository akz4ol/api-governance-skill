# Benchmarks

This directory contains performance benchmarks for api-governance-skill.

## Metrics Tracked

| Metric | Description | Target |
|--------|-------------|--------|
| Parse time | Time to parse OpenAPI spec | < 500ms for 100 operations |
| Rules time | Time to run all governance rules | < 1s for 100 operations |
| Diff time | Time to compute breaking changes | < 500ms for 100 operations |
| Memory peak | Maximum memory during processing | < 500MB |

## Running Benchmarks

```bash
# Run all benchmarks
./benchmark.sh

# Run specific benchmark
python benchmark_parser.py
```

## Test Specs

| Spec | Operations | Size |
|------|------------|------|
| `specs/small.yaml` | 10 | ~5KB |
| `specs/medium.yaml` | 50 | ~25KB |
| `specs/large.yaml` | 200 | ~100KB |
| `specs/xlarge.yaml` | 500 | ~250KB |

## Results

See [results.md](results.md) for latest benchmark results.

## Contributing

To add a benchmark:

1. Create `benchmark_<component>.py`
2. Use the `timeit` module for timing
3. Report results in standard format
4. Add to `benchmark.sh`

## CI Integration

Benchmarks run on every release tag. Results are compared against baseline to detect regressions.

Performance regressions > 20% will fail the build.
