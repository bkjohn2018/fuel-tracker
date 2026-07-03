# Fuel Retainage Training and Reference Bundle

Operational accounting onboarding and month-end reference for fuel usage and shipper retainage. These materials are principles-first and technology-agnostic; they teach the regulatory and accounting logic before mapping it to workbooks or systems.

## Scope and purpose

This bundle teaches the accounting and regulatory logic of fuel usage and shipper retainage independent of any specific tool or organization. FIRE is intended to support the election of **Option B** -- the tracker-with-true-up recovery method under 18 CFR 154.403 -- by providing the estimate and reconciliation layer a tracker requires. The materials here cover the surrounding people, process, and accounting layer. They do not assume a specific chart of accounts, tariff, or system; those bindings belong to a per-organization instantiation, not to this portable core.

## Artifacts

| Artifact | Markdown (source) | Office (deliverable) | Use |
|---|---|---|---|
| Accounting playbook | [Fuel_Retainage_Playbook.md](Fuel_Retainage_Playbook.md) | [Fuel_Retainage_Playbook.docx](Fuel_Retainage_Playbook.docx) | Month-end reference; regulatory and ASC 980 detail |
| Team onboarding deck | [Fuel_Retainage_Onboarding_Deck.md](Fuel_Retainage_Onboarding_Deck.md) | [Fuel_Retainage_Onboarding.pptx](Fuel_Retainage_Onboarding.pptx) | Slide content and speaker notes to present |
| Facilitator guide | [Fuel_Retainage_Facilitator_Guide.md](Fuel_Retainage_Facilitator_Guide.md) | [Fuel_Retainage_Facilitator_Guide.docx](Fuel_Retainage_Facilitator_Guide.docx) | How to run the onboarding session |
| Month-end checklist | [Fuel_Retainage_MonthEnd_Checklist.md](Fuel_Retainage_MonthEnd_Checklist.md) | [Fuel_Retainage_MonthEnd_Checklist.docx](Fuel_Retainage_MonthEnd_Checklist.docx) | Recurring month-end control; bridges principle to workbook |

## How they fit together

1. **Present** the onboarding deck to introduce vocabulary and the north-star principle.
2. **Facilitate** using the facilitator guide for prompts, timing, and the workbook tie-in exercise.
3. **Keep** the playbook as the team's ongoing reference for FERC rules, journal entries, and rate-management controls.
4. **Practice** with the month-end checklist each close to carry the principles into the workbook and surface drift early.

## Suggested session flow

- **Full session:** ~50 minutes (see facilitator guide Section 3).
- **Short version:** ~30 minutes (slides 1, 3, 6, 8, 10, 12, 15).
- **Workbook exercise:** add ~10 minutes (facilitator guide Section 6).

## Relationship to FIRE

FIRE (Fuel Integrity & Reconciliation Engine) is the technical estimate and reconciliation layer for compressor fuel (FERC Account 820). It forecasts fuel usage, validates against source snapshots, and preserves revision-aware lineage for audit.

This bundle covers the people, process, and accounting layer around fuel retainage:

- **Estimate and true-up** -- timely flash accruals, then correction to measured actuals
- **ASC 980 accounting** -- regulatory assets (182.3) and liabilities (254)
- **Rate management** -- resetting the retention percentage and clearing accumulated balances under 18 CFR 154.403

FIRE supports the estimate and reconciliation steps well. The playbook makes explicit the full closed loop -- including feeding measured over/under positions back into the tariff retention rate so fuel stays revenue-neutral. That rate-management step is not yet automated in FIRE (see README roadmap Phase 2).

## North star

> We can set our own fuel rate. We just can't profit from fuel.

Every artifact in this bundle returns to that principle.
