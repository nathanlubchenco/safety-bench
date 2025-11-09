#!/bin/bash
# Quick test script - demonstrates basic usage in under 1 minute

set -e

echo "========================================================================"
echo "WildGuard-Temporal: Quick Test (< 1 minute)"
echo "========================================================================"
echo ""

# Quick test with mock model
wildguard-temporal \
    --model mock \
    --scenario gradual-shift \
    --turns 20 \
    --shift-pattern linear \
    --evaluator keyword \
    --output quick_test_results \
    --format html json plot

echo ""
echo "Quick test complete! Check quick_test_results/ for outputs."
