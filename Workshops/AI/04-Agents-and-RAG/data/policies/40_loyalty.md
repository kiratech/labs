# Loyalty (LOY-400) — v1.0
Defines loyalty program rules: tiers, benefits, eligibility, voucher issuance and expiration, and extensions. Use for LOY-* queries and when calculating loyalty-related entitlements or voucher values.

## Tiers (LOY-41x)
- [LOY-411] Silver < 1000 pts; Gold 1000–4999; Platinum ≥ 5000.

## Benefits (LOY-42x)
- [LOY-421] Gold: free Standard shipping; returns **+7 days** on apparel/footwear.
- [LOY-422] Platinum: free Express; returns **+14 days** on apparel/footwear.

## Points (LOY-43x)
- [LOY-431] Earn 1 pt/€ (net of tax). No points on shipping or vouchers.
- [LOY-432] Redeem 100 pts = €1; cannot pay taxes/fees with points.
- [LOY-433] Points expire after 18 months of inactivity.

**Note**
[LOY-421]/[LOY-422] **extend** but do not remove other rules (e.g., restocking).
