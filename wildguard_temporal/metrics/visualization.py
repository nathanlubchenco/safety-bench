"""
Visualization utilities for temporal safety metrics.
"""

from typing import TYPE_CHECKING, Optional
import json

if TYPE_CHECKING:
    from wildguard_temporal.benchmark import BenchmarkResults


def plot_safety_trajectory(
    results: "BenchmarkResults",
    output_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot safety scores over conversation turns.

    Args:
        results: BenchmarkResults object
        output_path: Path to save figure (None = don't save)
        show: Whether to display the plot

    Returns:
        matplotlib figure object
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Install with: pip install matplotlib")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    turns = list(range(len(results.safety_scores)))
    scores = results.safety_scores

    # Plot safety scores
    ax.plot(turns, scores, 'b-', linewidth=2, label='Safety Score')

    # Add threshold line
    ax.axhline(y=results.metrics.threshold, color='r', linestyle='--',
               alpha=0.7, label=f'Safety Threshold ({results.metrics.threshold})')

    # Highlight failures
    failures = [i for i, s in enumerate(scores) if s < results.metrics.threshold]
    if failures:
        ax.scatter(failures, [scores[i] for i in failures],
                  color='red', s=100, zorder=5, label='Failures', marker='x')

    # Add trend line
    if len(scores) > 1:
        import numpy as np
        z = np.polyfit(turns, scores, 1)
        p = np.poly1d(z)
        ax.plot(turns, p(turns), "g--", alpha=0.5,
               label=f'Trend (slope={z[0]:.4f})')

    ax.set_xlabel('Conversation Turn', fontsize=12)
    ax.set_ylabel('Safety Score', fontsize=12)
    ax.set_title(f'Safety Over Time: {results.scenario_name}\n'
                f'Model: {results.model_name}', fontsize=14, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    # Add text box with metrics
    textstr = '\n'.join([
        f'Mean: {results.metrics.mean_safety_score:.3f}',
        f'Pattern: {results.metrics.degradation_pattern}',
        f'Failures: {results.metrics.failure_count}/{results.total_turns}',
    ])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")

    if show:
        plt.show()

    return fig


def plot_context_vulnerability(
    results: "BenchmarkResults",
    output_path: Optional[str] = None,
    show: bool = True,
):
    """
    Plot vulnerability by context position (for long-context scenarios).

    Args:
        results: BenchmarkResults object
        output_path: Path to save figure
        show: Whether to display the plot

    Returns:
        matplotlib figure object or None
    """
    if not results.metrics.position_vulnerability:
        print("No position vulnerability data available for this scenario.")
        return None

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed.")
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    regions = list(results.metrics.position_vulnerability.keys())
    vulnerabilities = list(results.metrics.position_vulnerability.values())

    bars = ax.bar(regions, vulnerabilities, color='steelblue', alpha=0.7)

    # Color code by severity
    colors = ['green' if v < 0.3 else 'orange' if v < 0.6 else 'red'
             for v in vulnerabilities]
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    ax.set_xlabel('Context Position', fontsize=12)
    ax.set_ylabel('Vulnerability Score', fontsize=12)
    ax.set_title(f'Safety Vulnerability by Context Position\n{results.scenario_name}',
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, (region, vuln) in enumerate(zip(regions, vulnerabilities)):
        ax.text(i, vuln + 0.02, f'{vuln:.2f}',
               ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")

    if show:
        plt.show()

    return fig


def generate_html_report(
    results: "BenchmarkResults",
    output_path: str = "report.html",
) -> str:
    """
    Generate comprehensive HTML report.

    Args:
        results: BenchmarkResults object
        output_path: Path to save HTML report

    Returns:
        Path to generated report
    """
    # Generate plots as base64 for embedding
    import io
    import base64

    # Safety trajectory plot
    fig1 = plot_safety_trajectory(results, show=False)
    if fig1:
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format='png', dpi=150, bbox_inches='tight')
        buf1.seek(0)
        import matplotlib.pyplot as plt
        plt.close(fig1)
        img1_base64 = base64.b64encode(buf1.read()).decode()
        trajectory_img = f'<img src="data:image/png;base64,{img1_base64}" style="max-width:100%"/>'
    else:
        trajectory_img = "<p>Trajectory plot not available</p>"

    # Context vulnerability plot
    fig2 = plot_context_vulnerability(results, show=False)
    if fig2:
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png', dpi=150, bbox_inches='tight')
        buf2.seek(0)
        import matplotlib.pyplot as plt
        plt.close(fig2)
        img2_base64 = base64.b64encode(buf2.read()).decode()
        vulnerability_img = f'<img src="data:image/png;base64,{img2_base64}" style="max-width:100%"/>'
    else:
        vulnerability_img = ""

    # Build HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WildGuard-Temporal Safety Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .plot-container {{
            margin: 20px 0;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        .safe {{ color: green; font-weight: bold; }}
        .unsafe {{ color: red; font-weight: bold; }}
        .warning {{ color: orange; font-weight: bold; }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ WildGuard-Temporal Safety Report</h1>
        <p><strong>Scenario:</strong> {results.scenario_name}</p>
        <p><strong>Model:</strong> {results.model_name}</p>
        <p><strong>Timestamp:</strong> {results.timestamp}</p>
    </div>

    <div class="section">
        <h2>📊 Key Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Mean Safety Score</div>
                <div class="metric-value">{results.metrics.mean_safety_score:.3f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Degradation Rate</div>
                <div class="metric-value">{results.metrics.degradation_rate:.4f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Turn to Failure</div>
                <div class="metric-value">{results.metrics.turn_to_failure if results.metrics.turn_to_failure else 'N/A'}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pattern</div>
                <div class="metric-value" style="font-size:1.2em;">{results.metrics.degradation_pattern}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Failures</div>
                <div class="metric-value">{results.metrics.failure_count}/{results.total_turns}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Evaluation Time</div>
                <div class="metric-value">{results.evaluation_time:.1f}s</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📈 Safety Trajectory</h2>
        <div class="plot-container">
            {trajectory_img}
        </div>
    </div>

    {f'''
    <div class="section">
        <h2>📍 Context Position Vulnerability</h2>
        <div class="plot-container">
            {vulnerability_img}
        </div>
    </div>
    ''' if vulnerability_img else ''}

    <div class="section">
        <h2>🔍 Detailed Analysis</h2>
        <pre>{results.metrics.summary()}</pre>
    </div>

    <div class="section">
        <h2>⚙️ Configuration</h2>
        <pre>{json.dumps(results.scenario_metadata, indent=2)}</pre>
    </div>

    <div class="section">
        <h2>💬 Conversation Sample (First 5 Turns)</h2>
        <table>
            <tr>
                <th>Turn</th>
                <th>Role</th>
                <th>Content</th>
                <th>Safety Score</th>
            </tr>
            {_generate_conversation_rows(results, max_turns=5)}
        </table>
    </div>

</body>
</html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated HTML report: {output_path}")
    return output_path


def _generate_conversation_rows(results: "BenchmarkResults", max_turns: int = 5) -> str:
    """Helper to generate HTML table rows for conversation."""
    rows = []
    for i, turn in enumerate(results.conversation[:max_turns * 2]):  # *2 for user+assistant
        if turn['role'] == 'user':
            turn_num = i // 2 + 1
            safety_score = results.safety_scores[i // 2] if i // 2 < len(results.safety_scores) else None
        else:
            turn_num = ""
            safety_score = ""

        # Truncate long content
        content = turn['content']
        if len(content) > 200:
            content = content[:200] + "..."

        # Color code safety
        if isinstance(safety_score, float):
            if safety_score >= 0.7:
                safety_class = "safe"
            elif safety_score >= 0.4:
                safety_class = "warning"
            else:
                safety_class = "unsafe"
            safety_display = f'<span class="{safety_class}">{safety_score:.3f}</span>'
        else:
            safety_display = ""

        rows.append(f"""
            <tr>
                <td>{turn_num}</td>
                <td><strong>{turn['role']}</strong></td>
                <td>{content}</td>
                <td>{safety_display}</td>
            </tr>
        """)

    return "\n".join(rows)
