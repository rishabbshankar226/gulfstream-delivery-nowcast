# Brief: claims, risks to GD's business (prefix `risk-`)

Output: `docs/build/claims_risks.json`. Cache folder: `data/raw/sources/risks/`.

From GD's 2025 10-K (accession 0000040533-26-000006, file `gd-20251231.htm`, Item 1A Risk Factors) and, where useful, GD's 2025 and 2026 earnings calls, one claim for each risk the source states:
1. Business-jet demand depending on economic conditions, and its effect on Aerospace.
2. Supply chain disruption affecting production or deliveries.
3. Certification, development and production ramp of new aircraft models.
4. Customer order cancellations, deferrals or defaults on aircraft orders.
5. Dependence on US government spending and budget decisions for the defense segments.
6. Fixed-price contracts and cost overruns.
7. Tariffs or trade policy, if GD's filings or calls name them.
8. International sales and foreign exchange, if stated.

Each `text` names the risk as GD states it, in one sentence; never add a probability or a size GD did not state. Then read `docs/build/briefs/_claims_common.md` and follow it exactly.
