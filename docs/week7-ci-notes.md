# Week 7 — CI and GitHub Notes

## Why CI Tests Must Not Depend on Real API Keys

CI runs on pull requests, including branches that may not have access to repository secrets. Tests that require real API keys would therefore fail unnecessarily or encourage developers to expose credentials in source code.

The deterministic test suites use mocks, fakes and local test infrastructure instead. This allows pull requests to be tested safely without giving untrusted branches access to production credentials.

## Why the Real-LLM Evaluation Suite Should Not Run on Every Push

Running the real-LLM evaluation suite on every push would increase cost and significantly slow down CI. Model responses can also be non-deterministic, which could cause flaky builds even when the application code is correct. Real-model evaluations may require API keys or external services that should not be exposed to every pull request, so the evaluation suite is better run manually and its results recorded separately.

## Required Status Checks

The `main` branch is protected using required GitHub status checks.

The required CI checks are:

- `dotnet`
- `angular`
- `python`

A pull request cannot be merged until all required checks pass.