"""Prometheus-style metrics collection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CounterMetric:
    name: str
    help_text: str
    value: int = 0
    labels: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def inc(self, amount: int = 1, **labels) -> None:
        self.value += amount
        if labels:
            key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            self.labels[key] += amount

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help_text}", f"# TYPE {self.name} counter", f"{self.name} {self.value}"]
        for key, val in self.labels.items():
            lines.append(f'{self.name}{{{key}}} {val}')
        return "\n".join(lines)


@dataclass
class GaugeMetric:
    name: str
    help_text: str
    value: float = 0.0

    def set(self, value: float) -> None:
        self.value = value

    def inc(self, amount: float = 1.0) -> None:
        self.value += amount

    def dec(self, amount: float = 1.0) -> None:
        self.value -= amount

    def render(self) -> str:
        return f"# HELP {self.name} {self.help_text}\n# TYPE {self.name} gauge\n{self.name} {self.value}"


@dataclass
class HistogramMetric:
    name: str
    help_text: str
    buckets: List[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    counts: List[int] = field(default_factory=list)
    total: float = 0.0
    count: int = 0

    def __post_init__(self) -> None:
        if not self.counts:
            self.counts = [0] * (len(self.buckets) + 1)

    def observe(self, value: float) -> None:
        self.total += value
        self.count += 1
        for i, b in enumerate(self.buckets):
            if value <= b:
                self.counts[i] += 1
                return
        self.counts[-1] += 1

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help_text}", f"# TYPE {self.name} histogram"]
        cumulative = 0
        for i, b in enumerate(self.buckets):
            cumulative += self.counts[i]
            lines.append(f'{self.name}_bucket{{le="{b}"}} {cumulative}')
        cumulative += self.counts[-1]
        lines.append(f'{self.name}_bucket{{le="+Inf"}} {cumulative}')
        lines.append(f"{self.name}_sum {self.total}")
        lines.append(f"{self.name}_count {self.count}")
        return "\n".join(lines)


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: Dict[str, CounterMetric] = {}
        self._gauges: Dict[str, GaugeMetric] = {}
        self._histograms: Dict[str, HistogramMetric] = {}

    def counter(self, name: str, help_text: str = "") -> CounterMetric:
        if name not in self._counters:
            self._counters[name] = CounterMetric(name=name, help_text=help_text)
        return self._counters[name]

    def gauge(self, name: str, help_text: str = "") -> GaugeMetric:
        if name not in self._gauges:
            self._gauges[name] = GaugeMetric(name=name, help_text=help_text)
        return self._gauges[name]

    def histogram(self, name: str, help_text: str = "") -> HistogramMetric:
        if name not in self._histograms:
            self._histograms[name] = HistogramMetric(name=name, help_text=help_text)
        return self._histograms[name]

    def render_all(self) -> str:
        parts = []
        for m in self._counters.values():
            parts.append(m.render())
        for m in self._gauges.values():
            parts.append(m.render())
        for m in self._histograms.values():
            parts.append(m.render())
        return "\n\n".join(parts) + "\n"

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _registry


# Pre-defined metrics
REQUEST_COUNT = _registry.counter("http_requests_total", "Total HTTP requests")
REQUEST_DURATION = _registry.histogram("http_request_duration_seconds", "HTTP request duration")
ACTIVE_USERS = _registry.gauge("active_users", "Number of active users")
PREDICTIONS_TOTAL = _registry.counter("predictions_total", "Total predictions made")
