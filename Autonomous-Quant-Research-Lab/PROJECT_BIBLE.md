# AQRL Project Bible

## 1. Mission

AQRL — Autonomous Quant Research Lab — is an institutional-grade research platform for systematic finance. Its mission is to discover, validate, explain, combine, and govern quantitative strategies using modern software engineering, statistical rigor, AI, game theory, multi-agent systems, and market simulation.

## 2. Core Philosophy

AQRL is not a trading script. It is a research operating system for financial intelligence.

The platform treats markets as:

- partially observable systems;
- adaptive multi-agent environments;
- non-stationary stochastic processes;
- regime-dependent networks of risk, liquidity, and information;
- domains where scientific validation matters as much as model performance.

## 3. Architectural Principles

1. Research and production must be separated.
2. Every experiment must be reproducible.
3. Every model must be registered and auditable.
4. Every strategy must be stress-tested.
5. Every architectural decision must be documented.
6. All core logic belongs in Python packages, not notebooks.
7. Notebooks are interfaces, not engines.
8. Dashboards visualize the system; they do not own business logic.
9. Execution modules default to paper trading.
10. No performance claim is accepted without out-of-sample validation.

## 4. System Layers

### 4.1 Infrastructure Kernel
Responsible for configuration, logging, event bus, registries, plugin loading, scheduling, typing, exceptions, and shared utilities.

### 4.2 Financial Core
Responsible for market data, features, market state, portfolio construction, optimization, risk, execution abstractions, and backtesting.

### 4.3 Intelligence Layer
Responsible for agents, game theory, world models, digital twin, LLM assistance, and alpha discovery.

### 4.4 Application Layer
Responsible for Streamlit dashboards, notebooks, CLI tools, APIs, and reports.

## 5. Research Discipline

AQRL requires a scientific pipeline:

Hypothesis → Implementation → Backtest → Walk-forward → Stress → Monte Carlo → Ablation → Paper Trading → Governance Review.

## 6. Financial Game Theory Vision

AQRL will support financial formulations of:

- WOP-CFR for adaptive decision-making under imperfect information;
- PM-PSRO for robust policy population mixing;
- market making and liquidity games;
- dynamic hedging games;
- portfolio allocation as policy selection under regime uncertainty.

## 7. Digital Twin Vision

AQRL will eventually provide a synthetic market where agents interact under different liquidity, volatility, information, and execution regimes.

## 8. Governance

All models, policies, datasets, and experiments must be versioned. The platform must be capable of answering:

- which dataset produced this result?
- which parameters were used?
- which strategy version was tested?
- which stress scenarios failed?
- why was this policy accepted or rejected?

## 9. Immediate Development Rule

Do not implement advanced trading algorithms before the foundation is stable.

The development order is:

1. Repository bootstrap
2. Core infrastructure
3. Data layer
4. Market state
5. Portfolio engine
6. Risk engine
7. Research OS
8. Regime engine
9. Game theory
10. Digital twin
11. Alpha discovery
12. Execution
13. Dashboard
