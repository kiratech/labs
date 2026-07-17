# Returns & Refunds (RET-100) — v1.0
Contains rules for returns and refunds: eligibility windows, DOA rules, bundle handling, allowed refund methods, and calculation/cap rules. Query this file for any RET-* clause, exact refund logic, and examples of how to compute refund amounts and apply caps.

## Windows (RET-1xx)
- [RET-101] Apparel/Footwear: 30 days from delivery; unused, with tags.
- [RET-102] Electronics (sealed): 14 days.
- [RET-103] Electronics (opened, fully working): 14 days; **10% restocking**.
- [RET-104] Accessories: 30 days if unopened; 14 days if opened.

## DOA & Defects (RET-11x)
- [RET-111] DOA within 14 days: free return label + **refund or replacement** (customer choice), **no restocking**.
- [RET-112] After 14 days: follow Warranty (not covered here; assume repair/replacement path).

## Bundles (RET-12x)
- [RET-121] Partial return only if items have standalone SKUs and promo terms allow.
- [RET-122] Refund for bundles is **pro-rated**; bundle savings may be lost.

## Refund Method (RET-13x)
- [RET-131] Refund to original payment; processing within 7 business days after inspection.

## Escalation (RET-14x)
- [RET-141] For **defects after 14 days**, open **returns** ticket per [TCK-521].
- [RET-142] For **bundle partial-return disputes**, open **returns** ticket per [TCK-522].
- [RET-143] For **refund processing delays > 10 business days**, open **returns** ticket per [TCK-523].
