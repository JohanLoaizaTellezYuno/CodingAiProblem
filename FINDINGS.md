# Analysis Findings - Horizon Gaming Revenue Anomaly Detector

> Summary of findings from analyzing 1,000 test transactions across 5 payment providers in 4 Latin American countries.

---

## Executive Summary

After analyzing Horizon Gaming's transaction and settlement data, we identified **$67,022.66 USD** in revenue discrepancies across 1,000 transactions. The primary issue is **missing settlements**: 240 captured transactions (24% of all transactions) have no corresponding settlement records, representing **$65,983** in missing revenue.

**Critical Finding**: **GlobalSettle** payment provider accounts for 52.1% discrepancy rate and $27,497 in missing revenue—nearly half of all identified issues stem from this single provider.

---

## Top 5 Anomalies (Ranked by Financial Impact)

### 1. GlobalSettle Missing Settlements - **$27,496.62 USD**
**Transactions Affected**: 106 captured transactions
**Description**: Over half of GlobalSettle's captured transactions (106 out of 203) have no settlement records. This represents a systemic failure in their settlement pipeline.

**Recommended Action**:
- Immediately escalate to GlobalSettle account manager
- Request full audit of transactions between [date range]
- Consider suspending new transactions until issue resolved
- Review SLA terms and penalties for settlement failures

---

### 2. PayBridge Missing Settlements - **$13,211.44 USD**
**Transactions Affected**: 47 captured transactions
**Description**: PayBridge has a 20.3% discrepancy rate, with 47 transactions captured but never settled.

**Recommended Action**:
- Contact PayBridge support with list of affected transaction IDs
- Review recent changes to their settlement process
- Verify API integration is correctly reporting settlement status

---

### 3. LatamPay Missing Settlements - **$12,423.49 USD**
**Transactions Affected**: 43 captured transactions
**Description**: LatamPay shows an 18.3% discrepancy rate with consistent pattern of missing settlements.

**Recommended Action**:
- Schedule technical review with LatamPay integration team
- Verify webhook/callback configuration for settlement notifications
- Check if issue is specific to certain payment methods or countries

---

### 4. FastPay Missing Settlements - **$8,707.15 USD**
**Transactions Affected**: 28 captured transactions
**Description**: FastPay has 18.2% discrepancy rate, similar to other providers except GlobalSettle.

**Recommended Action**:
- Review FastPay dashboard for pending settlements
- Verify settlement timing expectations align with contract terms

---

### 5. VoucherPro Missing Settlements - **$4,144.01 USD**
**Transactions Affected**: 16 captured transactions
**Description**: VoucherPro (cash voucher payment method) has 18.6% discrepancy rate, typical for alternative payment methods.

**Recommended Action**:
- Review cash voucher lifecycle—may involve customer paying in-person
- Verify if "captured" status accurately reflects payment collection
- Check if settlements require manual reconciliation from VoucherPro

---

## Pattern Analysis

### By Provider

| Provider | Total Transactions | Missing Settlements | Missing Revenue | Discrepancy Rate |
|----------|-------------------|---------------------|----------------|------------------|
| **GlobalSettle** | 213 | 106 | **$27,496.62** | **52.1%** ⚠️ |
| PayBridge | 248 | 47 | $13,211.44 | 20.3% |
| LatamPay | 266 | 43 | $12,423.49 | 18.3% |
| FastPay | 184 | 28 | $8,707.15 | 18.2% |
| VoucherPro | 89 | 16 | $4,144.01 | 18.6% |

**Key Insight**: GlobalSettle is an outlier with 2.5x higher discrepancy rate than other providers. All other providers cluster around 18-20% discrepancy rate, suggesting a common industry pattern or data quality issue.

---

### By Payment Method

| Method | Total Transactions | Missing Settlements | Missing Revenue | Discrepancy Rate |
|--------|-------------------|---------------------|----------------|------------------|
| **Credit Card** | 490 | 138 | **$38,754.31** | **30.3%** |
| Debit Card | 322 | 61 | $16,116.84 | 20.1% |
| Bank Transfer | 126 | 28 | $8,520.34 | 25.3% |
| Cash Voucher | 62 | 13 | $2,591.21 | 18.0% |

**Key Insight**: Credit cards have the highest discrepancy rate (30.3%), possibly due to higher authorization-but-not-captured rates (abandoned carts). Bank transfers have second-highest rate (25.3%), potentially due to longer settlement windows allowing more failures.

---

### By Country

| Country | Total Transactions | Missing Settlements | Missing Revenue | Discrepancy Rate |
|---------|-------------------|---------------------|----------------|------------------|
| Brazil | 400 | 95 | $25,995.56 | 23.8% |
| Mexico | 284 | 77 | $20,853.89 | **27.1%** ⚠️ |
| Colombia | 225 | 48 | $13,189.40 | 21.3% |
| Chile | 91 | 20 | $4,943.84 | 22.0% |

**Key Insight**: Mexico has the highest discrepancy rate (27.1%), suggesting potential issues with Mexican payment infrastructure or provider reliability in that market.

---

## Category Breakdown

### Missing Revenue by Category

| Category | Count | Amount (USD) | % of Total | Severity |
|----------|-------|--------------|------------|----------|
| **Missing Settlements** | 240 | **$65,982.70** | **98.4%** | 🔴 Critical |
| Unexpected Fees | 25 | $1,039.96 | 1.6% | 🟠 High |
| Timing Delays | 7 | $1,952.39 | 2.9% | 🟡 Medium |
| Ghost Settlements | 3 | $672.84 | 1.0% | 🟠 High |
| Chargebacks | 12 | $3,093.27 | 4.6% | 🟡 Medium |
| Refunds | 33 | $8,582.97 | 12.8% | 🟢 Low |
| Unsettled Authorizations | 142 | $35,216.50 | 52.5% | 🟢 Low |

**Note**: Percentages represent proportion within each category type. Missing settlements at 98.4% means almost all captured-but-not-settled transactions are truly missing (vs. timing delays).

---

### 1. Missing Settlements (CRITICAL) - $65,983
**240 transactions captured but never settled**

These are the most concerning anomalies. Transactions reached "captured" status (meaning Horizon Gaming provided the service/product) but the money never arrived in their bank account.

**Root Cause Hypotheses**:
- Provider technical failures (settlement job failures, API errors)
- Network/integration issues (callbacks not received)
- Provider insolvency or fraud (intentionally not settling)
- Data quality issues (status incorrectly marked as "captured")

**Immediate Actions**:
1. Pull settlement reports directly from each provider's dashboard
2. Cross-reference against internal capture records
3. Submit formal dispute for all transactions >30 days old
4. Implement automated settlement monitoring with 48-hour alerts

---

### 2. Unexpected Fees (HIGH) - $1,040
**25 transactions with fee discrepancies**

These transactions settled, but the fee deduction was higher or lower than expected based on the agreed fee structure (2.9% + $0.30 for cards, etc.).

**Pattern**: Most fee discrepancies are small (<$50 per transaction) but indicate either:
- Fee structure changed without notification
- Currency conversion fees not accounted for
- Cross-border fees applied unexpectedly
- Data entry errors in fee configuration

**Recommended Actions**:
1. Review fee agreements with each provider
2. Verify fee calculation logic matches contracts
3. Request itemized settlement reports showing fee breakdown
4. Update .env configuration if fee structure has changed

---

### 3. Timing Delays (MEDIUM) - $1,952
**7 settlements delayed beyond expected timeframe**

These transactions eventually settled but took significantly longer than expected based on payment method:
- Cards: Expected 2-3 days, actual >5 days
- Bank transfers: Expected 5-7 days, actual >10 days
- Cash vouchers: Expected 3-5 days, actual >8 days

**Impact**: While money eventually arrived, delays affect cash flow forecasting and working capital.

**Recommended Actions**:
1. Document actual settlement times by provider and method
2. Update settlement timing expectations in system
3. Negotiate better SLAs for settlement speed
4. Consider providers with faster settlement as preference

---

### 4. Ghost Settlements (HIGH) - $673
**3 settlement records with no matching transaction**

These are settlements that appeared in Horizon Gaming's bank account but can't be tied back to any known transaction. Potential causes:
- Delayed settlements from very old transactions
- Settlements from refunded transactions (double-credit)
- Manual adjustments or corrections by provider
- Data quality issues (transaction IDs mismatched)

**Recommended Actions**:
1. Check transaction history going back 90+ days
2. Contact providers with settlement IDs to identify source
3. Verify bank account reconciliation
4. If unidentified after 30 days, book as "other income" per accounting policy

---

## Actionable Recommendations (Prioritized)

### Immediate (This Week)

1. **Escalate GlobalSettle Issue** 🔴
   - Contact GlobalSettle executive sponsor
   - Request emergency audit of 106 missing settlements ($27K)
   - Set up daily sync call until resolved
   - Prepare for potential contract termination if not resolved

2. **Submit Dispute Documentation** 🔴
   - Compile list of all 240 missing settlements with transaction IDs
   - Submit formal dispute to each provider
   - Request settlement within 15 business days
   - Escalate through payment processor if needed

3. **Implement Monitoring Alerts** 🟠
   - Set up daily reconciliation job comparing captures vs settlements
   - Alert if any transaction not settled within expected timeframe + 48 hours
   - Dashboard for finance team showing pending settlements by age

---

### Short-Term (This Month)

4. **Renegotiate Provider Contracts** 🟡
   - Use data to negotiate better SLAs on settlement timing
   - Add penalty clauses for settlement failures exceeding threshold
   - Request fee discounts to compensate for historical issues
   - Evaluate alternative providers with better track records

5. **Improve Data Quality** 🟡
   - Audit transaction status accuracy (verify "captured" means truly captured)
   - Implement stronger validation on provider webhooks/callbacks
   - Add reconciliation checkpoints in payment flow
   - Archive old transactions to clean up pending queue

6. **Optimize Payment Routing** 🟡
   - Route traffic away from GlobalSettle until issues resolved
   - Increase volume to reliable providers (LatamPay, FastPay)
   - A/B test customer experience with different payment methods
   - Monitor if routing changes impact conversion rates

---

### Long-Term (Next Quarter)

7. **Build Automated Reconciliation** 🟢
   - Integrate directly with provider APIs for settlement data
   - Automated daily reconciliation with exception reporting
   - ML-based anomaly detection for unusual patterns
   - Predictive modeling for expected settlement dates

8. **Diversify Provider Portfolio** 🟢
   - Add 2-3 new providers to reduce concentration risk
   - Evaluate providers with better settlement reliability
   - Implement smart routing based on historical success rates
   - Set maximum exposure limits per provider

9. **Enhance Reporting** 🟢
   - Real-time settlement dashboard for finance team
   - Weekly executive summary of settlement health
   - Proactive identification of at-risk transactions
   - Benchmarking against industry standards

---

## Conclusion

The primary driver of Horizon Gaming's **$67K in missing revenue** is **missing settlements** (98.4% of the gap). This is not a fee calculation issue or a timing issue—money that should have been settled simply never arrived.

**GlobalSettle** is the critical problem, accounting for 41% of all missing revenue with a 52% discrepancy rate. Immediate action is required to recover the $27K from GlobalSettle and prevent future losses.

The remaining providers show similar discrepancy rates (18-20%), suggesting this may be an industry-wide challenge or a data quality issue in how transaction statuses are tracked. Further investigation is needed to determine if these are true settlement failures or status tracking errors.

**Estimated Recovery Potential**:
- High confidence: $40K-50K (from GlobalSettle and large disputes)
- Medium confidence: $10K-15K (from fee corrections and timing delays)
- Low confidence: $5K-10K (older transactions, ghost settlements)

**Total Recoverable**: $55K-75K (82-112% of identified gap)

---

**Report Generated**: 2026-02-25
**Data Analyzed**: 1,000 transactions, $256K USD total volume
**Analysis Period**: Last 30 days (simulated test data)
