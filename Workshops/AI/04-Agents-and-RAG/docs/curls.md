### 1) Delay ≥10 business days → logistics ticket + 25% voucher (cap €50) + free shipping

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"I had an issue with my order. Delivery is 11 business days late.","thread_id":"tool-tests-01"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` → `create_ticket(category="logistics")`
**Expected result:** Opens a **logistics** ticket ([TCK-511]). Grants a **25% voucher** + **free shipping credit** ([SLA-213]), **capped at €50** ([SLA-214]).
**Citations:** `[TCK-511], [SLA-213], [SLA-214]`.

---

### 2) Route delayed twice within 60 days → logistics ticket

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"The same route was late twice within the last 60 days. Please open a logistics ticket and summarize next steps with sources.","thread_id":"tool-tests-02"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` → `create_ticket("logistics")`
**Expected result:** Opens a **logistics** ticket for repeated route delays ([TCK-512]).
**Citations:** `[TCK-512]`.

---

### 3) Carrier investigation unresolved for 3 days → logistics ticket

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Carrier investigation is unresolved after 3 business days. Open a logistics ticket and cite the rule.","thread_id":"tool-tests-03"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` → `create_ticket("logistics")`
**Expected result:** Opens a **logistics** ticket for an unresolved carrier investigation (>3 days) ([TCK-513]).
**Citations:** `[TCK-513]`.

---

### 4) Confirmed loss + signature opt-out → refund/reshipment, no voucher, no ticket

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Express order €800, customer opted out of signature, package is confirmed lost. What do we grant? Do not open a ticket unless policy requires it.","thread_id":"tool-tests-04"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` (no `create_ticket`)
**Expected result:** **Refund or reshipment** ([SLA-231]); **no loss voucher** when signature was opted out ([SLA-232]); ticket optional but **not required** ([TCK-514]).
**Citations:** `[SLA-231], [SLA-232], [TCK-514]`.

---

### 5) Partial return dispute on bundle → returns ticket

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Customer disputes a partial return on a 3-item bundle with unclear promo terms. Open a returns ticket and explain the refund logic with sources.","thread_id":"tool-tests-05"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` → `create_ticket("returns")`
**Expected result:** Opens a **returns** ticket ([TCK-522]); partial return allowed only for **standalone SKUs** and eligible promotions ([RET-121]); **pro-rata** refund, potential bundle discount loss ([RET-122]).
**Citations:** `[TCK-522], [RET-121], [RET-122]`.

---

### 6) DOA headphones on day 7 → free label, refund/replacement, no restocking (no ticket)

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Headphones are defective on day 7. What is the exact process and any fees? Please cite the rules.","thread_id":"tool-tests-06"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies`
**Expected result:** **DOA within 14 days** → free return label + **refund or replacement**, **no restocking fee** ([RET-111]).
**Citations:** `[RET-111]`.

---

### 7) Open electronics on day 10 (€1,200) + 5-day delay → compute amounts

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Opened laptop (fully working) returned on day 10, price €1,200; delivery was 5 business days late. Compute the euros for restocking and voucher (respecting caps) and give the net outcome with citations.","thread_id":"tool-tests-07"}'
```

**Expected tools:** `search_policies` → `calc("0.10*1200")`
**Expected result:** Restocking **10% = €120** ([RET-103]); voucher **20%** ([SLA-212]) **capped at €50** ([SLA-214]) → voucher **€50**; **net refund** = €1,200 − €120 = **€1,080**, plus voucher **€50**.
**Citations:** `[RET-103], [SLA-212], [SLA-214]`.

---

### 8) Digital license activation failure on day 5 → returns ticket + refund

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Digital license shows a server-side activation error at day 5. If required, open a returns ticket and confirm refund eligibility with sources.","thread_id":"tool-tests-08"}' | jq -r '.final_answer'
```

**Expected tools:** `search_policies` → `create_ticket("returns")`
**Expected result:** Opens a **returns** ticket ([TCK-531]); **refund** for **faulty activation within 7 days** ([DIG-312]); reminder: no refund after usage ([DIG-311]).
**Citations:** `[TCK-531], [DIG-312], [DIG-311]`.

---

### 9) B2B pallet 3 days late, value €3,200 → compute voucher with B2B cap (€250, no ticket)

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"B2B pallet shipment arrived 3 business days late, PO value €3,200. Calculate the voucher per policy and cite the cap. Do not open a ticket unless required.","thread_id":"tool-tests-09"}'
```

**Expected tools:** `search_policies` → `calc("0.10*3200")`
**Expected result:** Pallet tolerance **+2 days** ([SLA-241]) → after 3 days, **10%** = **€320** ([SLA-211]) but **B2B cap €250 per PO** ([SLA-242]) → **€250**. Ticket **not required** (<10 days) ([TCK-511]).
**Citations:** `[SLA-241], [SLA-211], [SLA-242], [TCK-511]`.

---

### 10) Standard delivery 5 days late, order €180 → 20% voucher (no cap exceeded), no ticket

**curl**

```bash
curl -s http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Standard delivery was 5 business days late on an order of €180. Compute the voucher and cite the rule. Do not escalate unless required.","thread_id":"tool-tests-10"}'
```

**Expected tools:** `search_policies` → `calc("0.20*180")`
**Expected result:** Voucher **20% = €36** ([SLA-212]); **cap €50** not reached ([SLA-214]); no escalation (<10 days) ([TCK-511]).
**Citations:** `[SLA-212], [SLA-214], [TCK-511]`.
