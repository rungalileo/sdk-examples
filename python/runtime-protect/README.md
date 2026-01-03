# Runtime Protect Examples

This directory contains examples and utilities for working with Galileo Runtime Protect — Galileo’s real-time guardrail system for detecting unsafe content, enforcing policies, and augmenting LLM applications with runtime safety.

The goal of this folder is to provide progressively more advanced examples, starting with isolated Protect functionality (rules, metrics, stages) and eventually moving toward a full end-to-end chatbot example that logs to Galileo, invokes Protect, and demonstrates real application integration.

## Directory Structure

[custom_llm_metric_protect_test](./custom_llm_metric_protect_test/)
A focused, self-contained example demonstrating:

- How to create a custom LLM-based metric (e.g., PII detection) using the Galileo Python SDK

- How to register that metric with your Galileo org

- How to create a Protect stage that uses the custom metric

- How to test Protect rules against sample inputs

💡 Note:
This example tests Runtime Protect behavior, but does not implement a full chatbot or log anything to Galileo Observability.
It uses OpenAI only to evaluate the custom metric.

More details are inside the [README.md](./custom_llm_metric_protect_test/README.md)