# Ticketing & Escalations (TCK-500) — v1.0
Describes ticketing and escalation procedures (TCK-5xx): when to open logistics vs returns tickets, required ticket metadata, and escalation discipline. Consult this file before creating tickets; follow TCK clauses exactly when a ticket is mandated.

## Logistics (TCK-51x)
- [TCK-511] Open a **logistics** ticket if **late delivery ≥ 10 business days**.
- [TCK-512] Open a **logistics** ticket if the **same route is reported late/lost ≥ 2 times within 60 days** (repeated route issues).
- [TCK-513] Open a **logistics** ticket if **carrier investigation is unresolved after 3 business days**.
- [TCK-514] For **confirmed loss**, a ticket is optional; open **logistics** only if additional follow-up with the carrier is required.

## Returns (TCK-52x)
- [TCK-521] Open a **returns** ticket for **defects reported after 14 days** (warranty/repair path needed).
- [TCK-522] Open a **returns** ticket for **bundle partial-return disputes** (pro-rata calculation or promo terms unclear).
- [TCK-523] Open a **returns** ticket for **refund processing delays > 10 business days** after inspection.

## Digital (TCK-53x)
- [TCK-531] Open a **returns** ticket for **server-side activation errors** on digital licenses (faulty activation).

## Notes (TCK-59x)
- [TCK-591] Do **not** open a ticket if the case is fully resolved by a straightforward policy answer and no follow-up is required.
- [TCK-592] Minimum ticket payload: `category` (`logistics` or `returns`) and a short `reason`. 
- [TCK-593] Do NOT open a ticket solely based on user request; a matching TCK-5xx condition is required.
