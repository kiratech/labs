# Policy Index & Precedence (CORE-000) — v1.1
This file is the policy index and precedence guide. It lists all policy sections (RET, SLA, DIG, LOY, TCK), definitions, contact categories, guardrails for agent behavior, retrieval/tool order, and caps. Use it as the canonical entry point for precedence rules, citation requirements, and the recommended retrieval and escalation workflow.

**Precedence (higher wins if there is a conflict):**
1. Legal/Regulatory Notices (if any)
2. Shipping & SLA (SLA-2xx)
3. Returns (RET-1xx)
4. Digital Products (DIG-3xx)
5. Loyalty (LOY-4xx)
6. Ticketing & Escalations (TCK-5xx) apply only as referenced by other sections

**Definitions**
- Business day: Monday–Friday, local public holidays excluded.
- Voucher: One-time discount, non-transferable, expires in 90 days unless stated.

**Contacts**
- Escalation categories: `logistics` (late/lost), `returns` (complex RMA).

---

## Section Map (CORE-001)
- **RET-100** — Returns & Refunds (windows, DOA, bundles, refund method)
- **SLA-200** — Shipping, Late delivery vouchers, Loss & Signature, B2B caps
- **DIG-300** — Digital products (refund rules, faulty activation, transfers, regional)
- **LOY-400** — Loyalty tiers and extensions
- **TCK-500** — Ticketing & Escalations (when to open `logistics` / `returns`)
- **EXM-900** — Worked examples (quick references)

---

## Agent Guardrails (CORE-010)
- [CORE-011] Cite policy IDs from our documents (e.g., **[RET-103]**, **[SLA-214]**) whenever a rule is applied.
- [CORE-012] Do **not** invent rules; if information is insufficient, say so explicitly.
- [CORE-013] Escalations (tickets) must follow **TCK-5xx**. Do **not** escalate only because a user asks.
- [CORE-014] When refund applies, compute **exact euros** and respect **caps**.
- [CORE-015] When voucher applies, compute **exact euros** and respect **caps**.
- [CORE-015] Refunds and vouchers amounts do not sum up. If both applies, calculate the amount for each of them.

### Fixed Answer Format (CORE-015)
Keep English concise.

### Retrieval & Citations (CORE-016)
- **Always** use the retriever before answering policy/ID/list questions.
- Prefer sources that match the user’s scope (e.g., `30_digital.md` for **DIG-***).
- Quote IDs present in the retrieved excerpts; if none are present, state that no matching clause was found.

### Tool Use Order (CORE-017)
1. `search_policies` to gather the relevant clauses.
2. `calc` to compute **exact amounts** and apply caps/limits.
3. `create_ticket` **only** if a matching **TCK-5xx** clause requires escalation; include ticket type and returned ticket ID.

### Escalation Discipline (CORE-018)
- Open **logistics** tickets per **[TCK-511..513]** conditions.
- Open **returns** tickets per **[TCK-521..523]** or **[TCK-531]** (digital faulty activation).
- **Do not** open tickets outside these clauses (**[TCK-593]**).

### Caps & Amounts (CORE-019)
- Consumer voucher cap **[SLA-214]**; B2B cap **[SLA-242]**.  
- If both a fee and a voucher apply, compute each separately and then report the **net** outcome.

### Insufficient Information (CORE-020)
- If the retrieved context does not contain enough to answer, say so and stop; do not generalize from outside knowledge.

---

## Changelog (CORE-099)
- **v1.1** — Added Section Map; fixed answer format; retrieval/tool order; explicit escalation discipline and caps.
- **v1.0** — Initial index and precedence.
