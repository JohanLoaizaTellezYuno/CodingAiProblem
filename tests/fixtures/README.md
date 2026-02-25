# Test Fixtures

This directory contains test data fixtures for unit and integration testing.

## Test Data Files

### test_transactions.csv

Contains 15 sample transactions with the following characteristics:

**Normal Captured Transactions (have settlements):**
- TXN_001: 100 BRL, credit card - has settlement SET_001
- TXN_002: 200 MXN, debit card - has settlement SET_002
- TXN_003: 500 COP, bank transfer - has settlement SET_003
- TXN_004: 150 CLP, cash voucher - has settlement SET_004
- TXN_009: 600 MXN, bank transfer - has settlement SET_009
- TXN_010: 1000 COP, credit card - has settlement SET_010
- TXN_013: 800 BRL, credit card - has settlement SET_013 (DELAYED - 18 days)
- TXN_014: 550 CLP, cash voucher - has settlement SET_014
- TXN_015: 900 MXN, credit card - has settlement SET_015

**Missing Settlements (RED FLAG):**
- TXN_005: 300 BRL, credit card, captured - NO SETTLEMENT
- TXN_008: 400 BRL, credit card, captured - NO SETTLEMENT

**Not Applicable (should not have settlements):**
- TXN_006: 75 BRL, authorized (not captured) - no settlement expected
- TXN_007: 250 MXN, declined - no settlement expected

**Refunds/Chargebacks:**
- TXN_011: 350 BRL, refunded - no settlement expected
- TXN_012: 450 MXN, chargedback - no settlement expected

### test_settlements.csv

Contains 10 settlement records:

**Matched Settlements:**
- SET_001 through SET_004: Normal settlements with correct fees
- SET_009, SET_010: Bank transfer and credit card settlements
- SET_013: DELAYED settlement (18 days after transaction - timing anomaly)
- SET_014, SET_015: Cash voucher and credit card settlements

**Ghost Settlement:**
- SET_999: Settlement for TXN_999 which doesn't exist in transactions

## Expected Test Outcomes

### Reconciliation Results

**Total Transactions:** 15
**Captured Transactions:** 9
**Matched Settlements:** 9
**Missing Settlements:** 2 (TXN_005, TXN_008)
**Ghost Settlements:** 1 (SET_999)
**Timing Anomalies:** 1 (TXN_013 - 18 days delay for credit card)

### Fee Calculation Expected Values

**Credit Card (2.9% + $0.30):**
- 100 BRL: 3.20 fee → 96.80 settlement
- 400 BRL: 11.90 fee → 388.10 settlement
- 800 BRL: 23.50 fee → 776.50 settlement
- 900 MXN: 26.40 fee → 873.60 settlement
- 1000 COP: 29.30 fee → 970.70 settlement

**Debit Card (2.9% + $0.30):**
- 200 MXN: 6.10 fee → 193.90 settlement

**Bank Transfer (1.5%):**
- 500 COP: 7.50 fee → 492.50 settlement
- 600 MXN: 9.00 fee → 591.00 settlement

**Cash Voucher (3.5%):**
- 150 CLP: 5.25 fee → 144.75 settlement
- 550 CLP: 19.25 fee → 530.75 settlement

### Anomaly Categories

**Missing Settlements (Critical):**
- Count: 2
- Amount: 700 BRL (TXN_005: 300 + TXN_008: 400)
- USD Equivalent: ~140 USD (at 0.20 rate)

**Timing Delays (Medium):**
- Count: 1
- Transaction: TXN_013 (800 BRL, 18 days to settle vs 2-3 day norm)

**Ghost Settlements (High):**
- Count: 1
- Settlement: SET_999 (100 BRL, no matching transaction)

**Not Applicable:**
- Authorized only: 1 (TXN_006)
- Declined: 1 (TXN_007)
- Refunded: 1 (TXN_011)
- Chargedback: 1 (TXN_012)

## Usage in Tests

These fixtures are designed to test:

1. **Exact matching**: Transaction ID matches settlement ID
2. **Missing settlement detection**: Captured transactions without settlements
3. **Ghost settlement detection**: Settlements without matching transactions
4. **Timing anomaly detection**: Settlements that take too long
5. **Status filtering**: Proper handling of authorized, declined, refunded, chargedback
6. **Fee calculation**: Correct fee deduction across all payment methods
7. **Multi-currency handling**: BRL, MXN, COP, CLP transactions
8. **Multi-provider handling**: PayBridge, LatamPay, GlobalSettle, FastPay
9. **Multi-country handling**: Brazil, Mexico, Colombia, Chile

## Data Integrity Notes

- All timestamps are in YYYY-MM-DD HH:MM:SS format (UTC assumed)
- Settlement dates are 2-20 days after transaction dates
- Currencies match between transactions and their settlements
- Providers match between transactions and their settlements
- Customer IDs are unique per transaction
- Transaction and settlement IDs follow TXN_XXX and SET_XXX patterns
