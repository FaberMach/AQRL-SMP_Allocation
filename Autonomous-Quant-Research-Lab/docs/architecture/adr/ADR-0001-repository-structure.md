# ADR-0001: Repository Structure

## Status
Accepted

## Context
AQRL is expected to grow into a large, modular research platform. A flat script-based layout would not scale.

## Decision
Use a Python package-centered layout with separate folders for documentation, tests, notebooks, scripts, configs, docker, and GitHub workflows.

## Consequences
- Encourages reusable code.
- Allows tests and CI from the start.
- Keeps notebooks as interfaces rather than core logic.
