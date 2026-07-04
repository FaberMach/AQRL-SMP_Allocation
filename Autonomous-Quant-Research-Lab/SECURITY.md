# Security Policy

AQRL may eventually integrate with market data providers, brokers, and execution APIs. Security must be treated as a first-class concern.

## Rules

- Never commit credentials.
- Never hardcode API keys.
- Use environment variables or secrets managers.
- Broker/execution modules must default to paper trading.
- Live trading must require explicit opt-in configuration.

## Reporting

Open a private security issue or contact the repository maintainer.
