sensitivity: internal
# Risk & Compliance — Data Privacy Policy Summary

## Data minimization
Systems and staff should collect and retain only the customer data necessary for the
specific banking purpose being served. AI assistants must not request, store, or log
raw personally identifiable information (PII) such as full card numbers, SSNs, or
account numbers when a masked or tokenized reference will do.

## PII handling in AI systems
Any AI system that processes customer text must run inbound and outbound PII detection.
Detected PII must be redacted before being used in a prompt, before being logged, and
before being returned in a response, unless the specific field is the minimum necessary
data for the transaction the customer explicitly initiated (e.g., last four digits of a
card for identity confirmation).

## Data subject rights
Customers may request access to, correction of, or deletion of their personal data,
subject to regulatory retention requirements (e.g., BSA/AML recordkeeping). Requests
must be routed to the Privacy Office and fulfilled within the statutory window
applicable to the customer's jurisdiction (e.g., 30 days under GDPR-aligned processes).

## Cross-border and cross-tenant data handling
Customer data belonging to one brand, subsidiary, or business unit must never be
accessible to, or used to answer queries from, another business unit's systems or staff
without an explicit, documented data-sharing agreement and a legitimate business
purpose. This applies equally to AI retrieval systems: a tenant's knowledge base and
customer data must be logically isolated from every other tenant's.

## Vendor and third-party model use
Any third-party AI/LLM provider used to process customer data must be under a signed
data processing agreement prohibiting use of bank data for third-party model training,
and must be reviewed by Risk & Compliance before production use.
