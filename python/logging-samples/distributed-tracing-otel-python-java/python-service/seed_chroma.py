"""Seed ChromaDB with sample financial services documents."""

import os
import sys
import time

import chromadb
import chromadb.utils.embedding_functions as ef

COLLECTION = "financial_docs"

DOCUMENTS = [
    {
        "id": "wire-transfer-policy",
        "text": (
            "Wire Transfer Policy: Account holders may initiate domestic wire transfers "
            "up to $50,000 per business day through online banking or by visiting a branch. "
            "International wires require additional verification and are limited to $25,000 "
            "per transaction. All wire transfers are subject to fraud screening and may be "
            "held for up to 24 hours for compliance review. Fees: $25 domestic, $45 international."
        ),
    },
    {
        "id": "fraud-detection-alerts",
        "text": (
            "Fraud Detection & Alerts: Our real-time fraud monitoring system analyzes "
            "transactions using machine learning models that evaluate spending patterns, "
            "geographic location, merchant category, and transaction velocity. Alerts are "
            "triggered when anomaly scores exceed the configured threshold. Customers receive "
            "SMS and push notifications within 30 seconds of a flagged transaction. False "
            "positive rates are maintained below 2% through continuous model retraining."
        ),
    },
    {
        "id": "account-types-overview",
        "text": (
            "Account Types Overview: We offer Checking, Savings, Money Market, and Certificate "
            "of Deposit (CD) accounts. Checking accounts include Standard (no minimum balance, "
            "$12/month fee) and Preferred ($5,000 minimum, no fee, 0.01% APY). Savings accounts "
            "earn 0.05% APY with a $300 minimum. Money Market accounts require $10,000 minimum "
            "and earn tiered rates from 0.10% to 0.25% APY. CDs range from 3-month to 5-year terms."
        ),
    },
    {
        "id": "mortgage-lending-guidelines",
        "text": (
            "Mortgage Lending Guidelines: Conventional mortgage applications require a minimum "
            "credit score of 620, debt-to-income ratio not exceeding 43%, and a down payment of "
            "at least 3% for first-time buyers or 5% for subsequent purchases. Jumbo loans "
            "(above $726,200) require 10% down and a 700+ credit score. Rate locks are available "
            "for 30, 45, or 60 days. Pre-approval letters are valid for 90 days from issuance."
        ),
    },
    {
        "id": "api-integration-guide",
        "text": (
            "API Integration Guide: Our Open Banking API follows the FDX 6.0 standard and provides "
            "RESTful endpoints for account information, transaction history, and payment initiation. "
            "Authentication uses OAuth 2.0 with PKCE flow. Rate limits: 100 requests/minute for "
            "read operations, 20 requests/minute for write operations. Webhooks are available for "
            "real-time transaction notifications. SDKs are provided for Java, Python, and Node.js."
        ),
    },
    {
        "id": "compliance-kyc-aml",
        "text": (
            "KYC/AML Compliance: All new accounts require identity verification through our "
            "tiered KYC process. Tier 1 (basic) accepts government-issued photo ID and SSN "
            "verification. Tier 2 (enhanced) adds proof of address and source of funds "
            "documentation for accounts exceeding $250,000. Suspicious Activity Reports (SARs) "
            "are filed for transactions over $10,000 in cash or patterns suggesting structuring. "
            "Customer risk scores are reassessed quarterly."
        ),
    },
]


def seed():
    host = os.getenv("CHROMADB_HOST", "localhost")
    port = int(os.getenv("CHROMADB_PORT", "8000"))

    # Wait for ChromaDB to be ready
    client = None
    for attempt in range(30):
        try:
            client = chromadb.HttpClient(host=host, port=port)
            client.heartbeat()
            break
        except Exception:
            print(f"Waiting for ChromaDB at {host}:{port}... (attempt {attempt + 1})")
            time.sleep(2)

    if client is None:
        print("ERROR: Could not connect to ChromaDB", file=sys.stderr)
        sys.exit(1)

    # Delete existing collection if present, then create fresh
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    embedding_fn = ef.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small",
    )
    collection = client.create_collection(name=COLLECTION, embedding_function=embedding_fn)
    collection.add(
        ids=[d["id"] for d in DOCUMENTS],
        documents=[d["text"] for d in DOCUMENTS],
    )
    print(f"Seeded {len(DOCUMENTS)} documents into '{COLLECTION}' collection.")


if __name__ == "__main__":
    seed()
