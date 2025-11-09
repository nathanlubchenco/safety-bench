# WildGuard-Temporal: AI Safety Persistence Benchmark

A comprehensive benchmark for evaluating AI safety degradation across temporal and contextual dimensions.

## Overview

WildGuard-Temporal addresses critical gaps in AI safety evaluation by testing how safety mechanisms persist (or degrade) across:
- **Long multi-turn conversations** (50-200+ turns)
- **Extended context windows** (100K+ tokens)
- **Gradual manipulation scenarios** ("boiling frog" attacks)
- **Organic context drift** (natural conversation evolution)

### Key Research Gaps Addressed

1. **Temporal Safety Degradation**: Existing multi-turn benchmarks focus on adversarial jailbreaks but miss gradual normalization and rapport-based erosion
2. **Long-Context Safety Blind Spots**: No existing benchmark combines 100K+ token contexts with safety evaluation, despite known vulnerabilities
3. **Real-World Deployment Scenarios**: Tests realistic chatbot usage patterns vs. artificial adversarial attacks

## Features

- **Scenario Generators**: Programmatic generation of safety-testing conversations
  - Gradual topic shifting (safe → unsafe transitions)
  - Rapport-building scenarios (trust exploitation)
  - Long-context harmful content embedding
  - Organic conversation drift patterns

- **Flexible Evaluation**: Pluggable safety evaluators
  - Integration with existing safety classifiers (LlamaGuard, ShieldGemma, etc.)
  - Custom safety scoring functions
  - Multi-dimensional safety assessment

- **Comprehensive Metrics**:
  - Safety score per turn: S(t) ∈ [0,1]
  - Degradation rate: dS/dt
  - Turn-to-failure detection
  - Context-position vulnerability analysis

- **Extensible Architecture**: Designed for future extensions
  - Multi-agent scenarios (Phase 2)
  - Cross-modal safety testing
  - Custom scenario types

## Installation

```bash
pip install -e .
```

### Dependencies
- Python 3.9+
- numpy
- matplotlib (for visualization)
- Optional: transformers, openai (for model integration)

## Quick Start

```python
from wildguard_temporal import TemporalSafetyBenchmark
from wildguard_temporal.scenarios import GradualShiftScenario
from wildguard_temporal.evaluators import SimpleSafetyEvaluator

# Create benchmark
benchmark = TemporalSafetyBenchmark()

# Generate scenario
scenario = GradualShiftScenario(
    initial_topic="cooking techniques",
    target_topic="dangerous substances",
    num_turns=50
)

# Run evaluation
results = benchmark.evaluate(
    scenario=scenario,
    model=your_model,  # Any callable that takes conversation history
    evaluator=SimpleSafetyEvaluator()
)

# Analyze results
print(f"Turn to failure: {results.turn_to_failure}")
print(f"Average degradation rate: {results.degradation_rate:.4f}")
results.plot_safety_over_time()
```

## Benchmark Components

### 1. Scenario Types

#### Gradual Shift Scenarios
Tests safety against incremental topic transitions from safe to unsafe content.

```python
from wildguard_temporal.scenarios import GradualShiftScenario

scenario = GradualShiftScenario(
    initial_topic="home chemistry experiments",
    target_topic="explosive synthesis",
    num_turns=100,
    shift_pattern="exponential"  # linear, exponential, sigmoid
)
```

#### Rapport-Based Scenarios
Tests if safety degrades as the model builds rapport with users.

```python
from wildguard_temporal.scenarios import RapportBasedScenario

scenario = RapportBasedScenario(
    persona="friendly teacher",
    harmful_goal="extract sensitive information",
    num_turns=75
)
```

#### Long-Context Scenarios
Tests detection of harmful content embedded in long documents.

```python
from wildguard_temporal.scenarios import LongContextScenario

scenario = LongContextScenario(
    context_length=100000,  # tokens
    harmful_positions=[10000, 50000, 90000],
    benign_content_type="technical documentation"
)
```

### 2. Safety Evaluators

Built-in evaluators and easy integration with external classifiers:

```python
from wildguard_temporal.evaluators import (
    LlamaGuardEvaluator,
    KeywordBasedEvaluator,
    CompositeSafetyEvaluator
)

# Use external safety classifier
evaluator = LlamaGuardEvaluator(model_name="meta-llama/LlamaGuard-7b")

# Combine multiple evaluators
composite = CompositeSafetyEvaluator([
    LlamaGuardEvaluator(),
    KeywordBasedEvaluator(harm_categories=["violence", "illegal"])
])
```

### 3. Metrics and Analysis

```python
# Access detailed metrics
metrics = results.metrics

# Primary metrics
print(metrics.safety_scores)          # Per-turn safety scores
print(metrics.degradation_rate)       # Overall degradation
print(metrics.turn_to_failure)        # First unsafe turn

# Context-aware metrics (for long-context scenarios)
print(metrics.position_vulnerability)  # Safety by context position

# Pattern classification
print(metrics.degradation_pattern)    # linear, exponential, resistant, etc.

# Visualization
results.plot_safety_over_time()
results.plot_context_vulnerability()
results.generate_report(output_path="report.html")
```

## Benchmark Suite

Pre-configured benchmark suites for standardized evaluation:

```python
from wildguard_temporal import StandardBenchmarkSuite

suite = StandardBenchmarkSuite()

# Run full evaluation suite
results = suite.run_all(model=your_model)

# Generate leaderboard
suite.generate_leaderboard(results)
```

### Standard Scenarios

1. **Gradual-Shift-50**: 50-turn gradual topic shift (10 scenarios)
2. **Gradual-Shift-100**: 100-turn gradual topic shift (10 scenarios)
3. **Rapport-Building**: Trust-based safety erosion (15 scenarios)
4. **Long-Context-100K**: 100K token contexts with embedded harmful content (20 scenarios)
5. **Organic-Drift**: Natural conversation evolution (10 scenarios)

## Architecture

```
wildguard_temporal/
├── __init__.py
├── benchmark.py              # Core benchmark orchestration
├── scenarios/
│   ├── __init__.py
│   ├── base.py              # Base scenario class
│   ├── gradual_shift.py     # Gradual topic shifting
│   ├── rapport_based.py     # Rapport building scenarios
│   ├── long_context.py      # Long context scenarios
│   └── generators.py        # Conversation generators
├── evaluators/
│   ├── __init__.py
│   ├── base.py              # Base evaluator interface
│   ├── keyword_based.py     # Simple keyword evaluator
│   ├── classifier_based.py  # ML classifier integration
│   └── composite.py         # Multi-evaluator composition
├── metrics/
│   ├── __init__.py
│   ├── core.py              # Core metric calculations
│   ├── patterns.py          # Degradation pattern detection
│   └── visualization.py     # Plotting and reporting
└── utils/
    ├── __init__.py
    ├── context_builder.py   # Long context construction
    └── safety_taxonomy.py   # Safety category definitions
```

## Extensibility

### Adding Custom Scenarios

```python
from wildguard_temporal.scenarios import BaseScenario

class CustomScenario(BaseScenario):
    def generate_conversation(self):
        # Your scenario generation logic
        return conversation_turns

    def get_ground_truth_labels(self):
        # Expected safety labels per turn
        return labels
```

### Custom Evaluators

```python
from wildguard_temporal.evaluators import BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    def evaluate_turn(self, turn, context):
        # Your safety evaluation logic
        return safety_score  # 0.0 (unsafe) to 1.0 (safe)
```

## Research & Citation

This benchmark is based on research identifying critical gaps in AI safety evaluation:

- **Multi-turn safety**: Existing benchmarks (SafeMT, SafeDialBench) focus on adversarial attacks, not gradual degradation
- **Long-context safety**: No benchmark combines 100K+ tokens with safety evaluation despite known vulnerabilities
- **Real-world applicability**: Tests organic conversation patterns, not just adversarial scenarios

If you use this benchmark in your research, please cite:

```bibtex
@software{wildguard_temporal,
  title={WildGuard-Temporal: AI Safety Persistence Benchmark},
  author={Your Name},
  year={2025},
  url={https://github.com/nathanlubchenco/safety-bench}
}
```

## Future Roadmap

- **Phase 2**: Multi-agent temporal safety (SwarmSafe integration)
- **Phase 3**: Cross-modal safety persistence (vision + language)
- **Phase 4**: Adaptive adversarial scenarios
- **Phase 5**: Real-world deployment monitoring

## Contributing

Contributions welcome! Areas of interest:
- New scenario types
- Integration with additional safety classifiers
- Metric improvements
- Real-world case studies

## License

MIT License - see LICENSE file for details.
