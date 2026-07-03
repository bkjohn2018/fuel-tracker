# Accounting for Fuel Usage & Shipper Retainage
### A plain-language playbook for the Operational Accounting team
*Version 1.0 -- internal training and month-end reference*

---

## 1. The one idea to hold onto

Everything in this playbook flows from a single regulatory principle:

> **The rule, in plain English:** FERC lets us set our own fuel rate -- but we can't make any money off the activity. We are allowed to earn a regulated return on the pipeline we built and operate. We are **not** allowed to earn a return on the fuel and lost gas we retain from shippers. Fuel is a pass-through: collect what we burn and lose, no more, no less.

A pipeline burns gas to run its compressors, and some gas is lost or unaccounted-for along the way. Rather than buy that gas on the open market, the pipeline keeps a small slice of every shipper's gas in-kind -- the **fuel retention** (or "retainage") percentage -- stated in its FERC tariff. Retention rates across the industry run from a fraction of a percent to as high as 13%.

The catch is **symmetry**. If we retain *more* gas than we actually burn and lose, we have over-recovered -- and that surplus is not profit, it is money we owe back to shippers. If we retain *less*, we have under-recovered and may be allowed to collect the shortfall later. The whole accounting-and-rate machine described here exists to measure that gap and close it.

> **Where the team's gap is:** The tracker does the hard part well -- it estimates fuel usage and retainage and stabilizes those estimates. What it does not close on its own is the last step -- feeding the measured over/under position back into the tariff retention rate so the pipeline stays revenue-neutral on fuel. This playbook makes that loop explicit.

---

## 2. What FERC actually requires

Four rules govern fuel retainage. Know these and the accounting follows logically.

### 2.1 Rates must be "just and reasonable" (NGA Section 4)
Section 4 of the Natural Gas Act requires that every rate a pipeline charges be **just and reasonable**, and that the rate be on file with FERC before it is charged -- the *filed-rate doctrine*. You cannot bill a fuel percentage that is not in your effective tariff, and you cannot reach back and re-bill a closed period.

### 2.2 You have two ways to recover fuel -- pick one (the ANR rule)
In the *ANR Pipeline* decision, FERC gave pipelines exactly two options:

| Option | How it works | The trade-off |
|---|---|---|
| **A -- Fixed retention %** | Set the percentage in a full Section 4 rate case and leave it until the next rate case. | You keep any over-recovery and eat any under-recovery between cases. That's the efficiency incentive -- but no annual true-up. |
| **B -- Tracker with true-up** | Adjust the percentage periodically outside a rate case under 18 CFR 154.403, and reconcile actual vs. retained each period. | You may **never** over-recover. Every surplus or shortfall is trued up and refunded or collected. This is the option a fuel tracker implements. |

**Scope of this framework.** This playbook is written for the **Option B** election -- a tracker with true-up under 18 CFR 154.403, where rates are adjusted from measured over/under positions and the pipeline may never over-recover. That is a hard obligation, and it is the mechanism the estimate/true-up steps below assume. Confirm your tariff's recovery method before relying on the entries that follow: if you recover fuel through a fixed percentage (Option A), the true-up mechanics in this playbook do not apply.

### 2.3 Under a tracker, over-recovery is never allowed
> A pipeline that tracks its fuel costs *"should not in any circumstances be permitted to over-recover those costs."*
> -- FERC, *Fuel Retention Practices of Natural Gas Companies*, 72 FR 55762, P6

This is the regulatory source of "you can't make money off the activity." The true-up is the condition FERC attaches to letting us move the rate outside a rate case.

### 2.4 The plumbing: 18 CFR 154.403
- **State the percentage in the tariff** so shippers know exactly how much gas is retained per unit shipped -- Section 154.403(b).
- **Publish the method in the General Terms & Conditions** -- how the percentage is calculated, how often it changes, how surpluses/shortfalls are returned or collected -- Section 154.403(c).
- **Show actual monthly inflows and outflows** of gas when filing a new percentage or surcharge -- Section 154.403(d)(3).
- **No retroactive recovery** -- you cannot collect or refund for periods before the tracker language was effective -- Section 154.403(d)(4).

The true-up itself lives in Section 154.403(c)(11): the tariff must state whether the difference between gas actually used/lost and gas retained "will be recovered or returned in a future surcharge."

### 2.5 Where FERC sees the numbers: Form No. 2
Every major interstate pipeline files **FERC Form No. 2** annually, reporting gas received from shippers for fuel and gas actually used for compression, other operations, and lost-and-unaccounted-for. FERC computes each pipeline's net over/under-retention from Form 2. Your internal tracker should reconcile to what Form 2 will show.

> **Accuracy note:** FERC studied whether to mandate trackers/true-ups for everyone (Docket RM07-20-000, 2007) but *terminated* that inquiry in 2008 without a universal rule. The case-by-case ANR framework above is still the governing policy -- don't cite a blanket mandate that doesn't exist.

---

## 3. The two-step process

### Step 1 -- Estimate (the flash), from invoice/nomination data
1. Pull throughput and the tariff retention % -> compute estimated gas retained from shippers.
2. Estimate gas consumed for compression plus estimated L&U -> estimated fuel used.
3. Retained minus used = estimated over/under position; value it at the applicable gas price.
4. Book the estimated accrual. Best guess, on time, from the best data at close.

*It is a timely, complete recording of estimated fuel usage and retainage -- like a flash report. It is not the final answer.*

### Step 2 -- True up to actuals, from physical measurement
1. Take actual measured fuel used and L&U.
2. Recompute the actual over/under position: gas retained minus gas actually used/lost.
3. Compare to the Step 1 estimate -- the difference is the true-up adjustment.
4. Adjust the accrual and the tracker balance to the measured position.

After Step 2 the tracker balance is the measured amount over- or under-collected to date -- the bridge to both the accounting and the rate correction.

| | Step 1 -- Estimate | Step 2 -- True-up |
|---|---|---|
| **Data source** | Invoice / nomination | Physical measurement |
| **Nature** | Estimated -- timely flash | Actual -- measured |
| **Answers** | "What do we think we retained vs. used?" | "What did we actually retain vs. use?" |
| **Output** | Estimated accrual & tracker entry | Corrected tracker balance -> rate action |

---

## 4. The accounting: ASC 980

Rate-regulated pipelines apply **ASC 980, Regulated Operations** -- it lets the balance sheet hold amounts ordinary GAAP would run through earnings, because a regulator will settle them later through rates.

### 4.1 The two balance-sheet outcomes
| Position | What it means | How you account for it |
|---|---|---|
| **Over-recovered** (retained > used/lost) | We kept more gas than we burned and lost. Not profit -- an obligation. | **Regulatory liability.** Owe it back via a lower future retention % or a refund surcharge. |
| **Under-recovered** (retained < used/lost) | We burned and lost more than we kept. A cost we may collect later. | **Regulatory asset** -- but only if recovery is *probable*. |

A regulatory **liability** (over-recovery) is recorded as soon as you have it. A regulatory **asset** (under-recovery) is recorded only when recovery through future rates is *probable*.

### 4.2 Why a fuel tracker makes recovery "probable"
PwC's guidance is explicit that "strong indicators of probable recovery include ... the implementation of a **tracker mechanism** by the regulator." The same mechanism that forces you to refund surpluses is what supports booking a shortfall as an asset.

### 4.3 Illustrative journal entries
*Account names are illustrative -- map to your chart of accounts and the FERC Uniform System of Accounts.*

**Step 1 -- Estimated accrual (over-retained this period):**
| Account | Debit | Credit |
|---|---|---|
| Gas Used in Operations -- fuel & L&U (P&L) | XX | |
| &nbsp;&nbsp;Fuel Retention Recovery (contra-cost) | | XX |
| Fuel Retention Recovery (to clear surplus) | XX | |
| &nbsp;&nbsp;**Regulatory Liability -- Fuel Tracker (B/S)** | | **XX** |

**Step 2 -- True-up (measured surplus smaller than estimate):**
| Account | Debit | Credit |
|---|---|---|
| **Regulatory Liability -- Fuel Tracker (B/S)** | **XX** | |
| &nbsp;&nbsp;Gas Used in Operations / Fuel Recovery | | XX |

*If actuals came in higher than retained (under-recovery) and recovery is probable, debit a Regulatory Asset -- Fuel Tracker and credit Gas Used in Operations.*

**Settlement:** When the accumulated balance is cleared through the next rate action, the liability is worked off as shippers are charged a lower retention % or credited a refund surcharge. No gain or loss should hit earnings -- the accounting expression of "no profit from fuel."

---

## 5. A worked example, start to finish
One month, round numbers, gas valued at $3.00/Dth.

| Line | Volume (Dth) | Value ($) |
|---|---:|---:|
| Throughput for the month | 1,000,000 | -- |
| Tariff fuel retention % = 2.0% -> gas retained | 20,000 | 60,000 |
| Step 1 -- estimated fuel used + L&U | 18,500 | 55,500 |
| **Step 1 -- estimated OVER-recovery** | **1,500** | **4,500** |
| Step 2 -- actual fuel used + L&U | 19,200 | 57,600 |
| **Step 2 -- actual OVER-recovery** | **800** | **2,400** |
| True-up adjustment (reduce liability) | (700) | (2,100) |

- Step 1 booked a $4,500 regulatory liability -- the surplus we thought we retained.
- Measurement showed we actually burned/lost more, so the real surplus is only $2,400.
- The true-up removes $2,100 of liability: **Dr Regulatory Liability 2,100 / Cr Gas Used in Operations 2,100**.
- **Ending tracker balance: $2,400 regulatory liability** -- owed back to shippers, carried until the rate action returns it.

*Signal for rate management:* at 2.0% we retained 20,000 Dth but only needed ~19,200. Running rich by ~0.08 points this month. One month is noise; a sustained pattern is a rate problem.

---

## 6. Closing the loop: rate management
Measuring the gap isn't enough -- the organization has to move the tariff rate so the gap trends to zero. Two levers.

### 6.1 Reset the retention percentage (prospective)
Set the go-forward percentage so expected gas retained ~ expected gas used and lost. Under 18 CFR 154.403 you recompute the percentage from actual measured inflows/outflows over a defined look-back period and file the new number.
- Use measured actuals (not estimates) as the basis.
- Define and disclose the look-back period and formula in the GT&C.
- File the limited Section 4 adjustment; the new percentage is prospective only.

### 6.2 Clear the accumulated balance (the true-up surcharge)
- **Over-recovered (regulatory liability):** return it as a credit / negative surcharge.
- **Under-recovered (regulatory asset):** collect it as a positive surcharge, to the extent recovery is probable.
- You can only clear balances that accumulated *after* the tracker tariff language became effective.

### 6.3 The governing test, every cycle
> Over a reasonable, disclosed period, does gas retained roughly equal gas used and lost -- and is the accumulated tracker balance trending toward zero rather than growing? A persistent surplus is the exact condition FERC treats as impermissible over-recovery.

### 6.4 How the loop connects
| Stage | What happens |
|---|---|
| Estimate | Book timely estimated fuel used vs. retained -> preliminary tracker entry. |
| True-up | Replace estimate with measured actuals -> corrected over/under position. |
| Record (ASC 980) | Carry the position as a regulatory liability or asset. |
| Reset rate (Section 154.403) | Re-file the retention % from measured actuals so future retained ~ used. |
| Clear balance | Return or collect the accumulated balance via true-up surcharge; earnings impact nets to zero. |

---

## 7. Controls & common pitfalls
- **Reconcile estimates to actuals every period**; track the estimate-to-actual variance over time.
- **Roll the tracker balance forward monthly**, tied to the GL: opening + current over/under - amounts returned/collected = closing.
- **Reconcile to Form No. 2 annually.**
- **Re-assess ASC 980 eligibility** each period; confirm any under-recovery asset remains probable.
- **Watch the earnings line** -- fuel activity should net to zero, not produce a gain or loss.
- **Never let a surplus sit and grow** -- that's the fact pattern FERC and shippers challenge.
- **Document the rate method** so it matches the tariff GT&C and is reproducible for a Section 154.403 filing.

---

## 8. Glossary
| Term | Plain meaning |
|---|---|
| Fuel retention / retainage | Small % of gas kept in-kind from each shipper to cover compressor fuel and lost gas. |
| L&U (lost & unaccounted-for) | Gas lost through leaks, measurement error, or other losses -- recovered alongside fuel. |
| Tracker | Tariff mechanism that adjusts the fuel % periodically and reconciles over/under-recovery. |
| True-up | Reconciliation of gas retained vs. actually used/lost, returned or collected via surcharge. |
| Over- / under-recovery | Retaining more (or less) gas than actually used/lost. Over = owe shippers; under = may collect. |
| Regulatory asset / liability | ASC 980 balance-sheet items holding amounts a regulator will settle through future rates. |
| NGA Section 4 / Section 5 | Section 4: pipeline files rate changes (must be just & reasonable). Section 5: shippers/FERC challenge a rate. |
| Form No. 2 | Annual FERC financial/operational report; shows gas retained vs. used/lost. |
| 18 CFR 154.403 | Regulation governing periodic fuel-percentage adjustments and true-up surcharges. |
| Filed-rate doctrine | You may only charge the rate on file with FERC -- no off-tariff or retroactive billing. |

---

## 9. Sources
- Natural Gas Act Section 4, 15 U.S.C. 717c -- just and reasonable rates.
- FERC, *Fuel Retention Practices of Natural Gas Companies*, Notice of Inquiry, Docket No. RM07-20-000, 72 FR 55762 (Oct. 1, 2007) -- ANR two-option policy and the "no over-recovery" standard (proceeding terminated 2008; ANR framework still governing).
- *ANR Pipeline Co.*, 110 FERC para  61,069 (2005).
- 18 CFR 154.403 -- Periodic rate adjustments.
- FERC Order No. 637 -- principle that pipelines should not profit from tariff mechanisms.
- FERC Form No. 2 -- Annual Report of Major Natural Gas Companies.
- ASC 980, Regulated Operations (regulatory assets 980-340; regulatory liabilities 980-405).
- PwC, *Utilities and Power Companies Guide*, Chapter 17 -- Regulated Operations (June 2025).
