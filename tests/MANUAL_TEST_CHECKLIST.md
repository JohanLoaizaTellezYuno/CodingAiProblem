# Manual Testing Checklist

This checklist provides comprehensive manual validation steps for the Horizon Gaming Revenue Anomaly Detector project.

## Pre-Testing Setup

- [ ] Python 3.9+ installed and accessible
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Node.js 18+ installed (for dashboard)
- [ ] `.env` file configured with correct paths and parameters
- [ ] Project structure verified (all directories exist)

---

## 1. Pipeline Execution Testing

### 1.1 Data Generation

**Test**: Generate test data

```bash
cd /Users/johan/Documents/Coding\ AI/horizon-gaming-detector
python pipeline/generate_data.py
```

**Expected Results**:
- [ ] Script executes without errors
- [ ] `data/raw/transactions.csv` file created
- [ ] `data/raw/settlements.csv` file created
- [ ] Transactions file contains 500-1000 records
- [ ] Settlements file contains 70-80% of captured transaction count
- [ ] Data includes all required columns
- [ ] Multiple currencies present (BRL, MXN, COP, CLP)
- [ ] Multiple providers present (4-5 providers)
- [ ] Multiple transaction statuses present (captured, authorized, declined, refunded, chargedback)
- [ ] Settlement dates are after transaction dates

**Validation Commands**:
```bash
wc -l data/raw/transactions.csv
wc -l data/raw/settlements.csv
head -5 data/raw/transactions.csv
head -5 data/raw/settlements.csv
```

---

### 1.2 Reconciliation Pipeline

**Test**: Run reconciliation pipeline

```bash
python pipeline/reconcile.py
```

**Expected Results**:
- [ ] Script executes without errors
- [ ] Progress messages displayed for each step
- [ ] `data/processed/reconciled_data.csv` file created
- [ ] `data/processed/ghost_settlements.csv` file created
- [ ] Reconciled data contains all original transactions
- [ ] Settlement status column added
- [ ] Expected settlement amounts calculated
- [ ] Timing anomalies detected
- [ ] Missing settlements identified
- [ ] Ghost settlements identified

**Key Metrics to Verify**:
- [ ] Match rate is 70-80% for captured transactions
- [ ] Settlement status categories include: matched, missing, discrepancy, not_applicable
- [ ] Timing anomaly flags are boolean (True/False)
- [ ] Expected settled amounts are less than transaction amounts

**Validation Commands**:
```bash
head -20 data/processed/reconciled_data.csv
wc -l data/processed/reconciled_data.csv
wc -l data/processed/ghost_settlements.csv
```

---

### 1.3 Analysis Pipeline

**Test**: Run analysis pipeline

```bash
python pipeline/analyze.py
```

**Expected Results**:
- [ ] Script executes without errors
- [ ] `data/processed/insights.json` file created
- [ ] `data/processed/anomalies.json` file created
- [ ] Executive summary displayed in console
- [ ] Total missing revenue calculated
- [ ] Top 3 root causes identified
- [ ] Insights JSON contains all required sections
- [ ] Anomalies JSON is a list of prioritized anomalies

**Key Metrics to Verify**:
- [ ] Total missing revenue > $0
- [ ] Category breakdown includes all 7 categories
- [ ] Provider performance metrics calculated
- [ ] Anomalies sorted by financial impact
- [ ] Recommendations list is populated

**Validation Commands**:
```bash
cat data/processed/insights.json | python -m json.tool | head -50
cat data/processed/anomalies.json | python -m json.tool | head -50
```

---

### 1.4 Full Pipeline Execution

**Test**: Run complete pipeline

```bash
python pipeline/main.py
```

**Expected Results**:
- [ ] All steps execute in sequence
- [ ] No errors or exceptions
- [ ] All output files generated
- [ ] Console shows progress for each phase
- [ ] Final success message displayed

**Output Files to Verify**:
- [ ] `data/processed/reconciled_data.csv`
- [ ] `data/processed/ghost_settlements.csv`
- [ ] `data/processed/insights.json`
- [ ] `data/processed/anomalies.json`

---

## 2. Dashboard Functionality Testing

### 2.1 Dashboard Setup

**Test**: Install and start dashboard

```bash
cd dashboard
npm install
npm run dev
```

**Expected Results**:
- [ ] Dependencies install successfully
- [ ] No npm errors
- [ ] Development server starts
- [ ] Server runs on port 3000
- [ ] No console errors on startup

---

### 2.2 Dashboard Loading

**Test**: Open dashboard in browser

Navigate to: `http://localhost:3000`

**Expected Results**:
- [ ] Dashboard loads without errors
- [ ] No 404 or 500 errors
- [ ] No JavaScript console errors
- [ ] Page renders completely
- [ ] Loading states display correctly

---

### 2.3 Metrics Overview

**Test**: Verify metrics cards display

**Expected Results**:
- [ ] Total transaction volume displayed
- [ ] Total settled amount displayed
- [ ] Total discrepancy amount displayed
- [ ] Discrepancy percentage displayed
- [ ] Status indicators show correct colors (green/yellow/red)
- [ ] Numbers formatted with commas and decimals
- [ ] Currency symbols displayed (USD)

**Visual Checks**:
- [ ] Cards are aligned and styled consistently
- [ ] Text is readable and properly sized
- [ ] Icons/indicators are visible

---

### 2.4 Time Series Chart

**Test**: Verify time series visualization

**Expected Results**:
- [ ] Chart renders without errors
- [ ] X-axis shows dates
- [ ] Y-axis shows amounts
- [ ] Data points are visible
- [ ] Trend lines are clear
- [ ] Legend displays correctly
- [ ] Tooltip shows on hover
- [ ] Toggle between daily/weekly works (if implemented)

**Visual Checks**:
- [ ] Chart is responsive
- [ ] Colors are distinct and readable
- [ ] Axes are labeled

---

### 2.5 Breakdown Charts

**Test**: Verify breakdown visualizations

**Expected Results**:

**Provider Breakdown**:
- [ ] Bar chart displays all providers
- [ ] Bars show discrepancy amounts
- [ ] Provider names are readable
- [ ] Values are accurate

**Payment Method Breakdown**:
- [ ] Pie/bar chart displays all methods
- [ ] Percentages or amounts shown
- [ ] Legend is clear
- [ ] Colors are distinct

**Country Breakdown**:
- [ ] Chart displays all countries
- [ ] Transaction volume vs discrepancy shown
- [ ] Country names are readable

---

### 2.6 Anomaly Feed

**Test**: Verify anomaly table/list

**Expected Results**:
- [ ] Top 10-15 anomalies displayed
- [ ] Columns include: Date, Provider, Payment Method, Country, Type, Amount, Discrepancy, Action
- [ ] Severity indicators visible (critical/warning/info)
- [ ] Data is sortable (if implemented)
- [ ] Suggested actions are actionable
- [ ] Amounts formatted correctly

**Visual Checks**:
- [ ] Table is readable
- [ ] Rows are distinct
- [ ] Critical items highlighted

---

### 2.7 Filtering and Drill-Down

**Test**: Verify filter functionality (if implemented)

**Expected Results**:

**Date Range Filter**:
- [ ] Date picker appears
- [ ] Selecting date range updates all components
- [ ] Invalid ranges are prevented

**Provider Filter**:
- [ ] Multi-select dropdown works
- [ ] Selecting providers filters data
- [ ] "Select All" / "Clear All" works

**Country Filter**:
- [ ] Multi-select dropdown works
- [ ] Selecting countries filters data
- [ ] Charts update accordingly

**Payment Method Filter**:
- [ ] Multi-select dropdown works
- [ ] Selecting methods filters data
- [ ] All components update

**General Filter Behavior**:
- [ ] Filters combine correctly (AND logic)
- [ ] Filtered counts update
- [ ] Clear filters button works
- [ ] No errors when filtering edge cases

---

### 2.8 Responsive Design

**Test**: Verify dashboard on different screen sizes

**Expected Results**:
- [ ] Desktop (1920x1080): All components visible, good spacing
- [ ] Laptop (1366x768): Layout adjusts, no horizontal scroll
- [ ] Tablet (768x1024): Cards stack vertically, charts resize
- [ ] Mobile (375x667): Fully responsive, touch-friendly (if designed for mobile)

---

### 2.9 Export Functionality

**Test**: Verify export features (if implemented)

**CSV Export**:
- [ ] Export button visible
- [ ] Click triggers download
- [ ] CSV file downloads successfully
- [ ] CSV contains correct data
- [ ] Filename is descriptive

**PDF Export** (optional):
- [ ] Export button visible
- [ ] PDF generates successfully
- [ ] PDF is readable and formatted

---

## 3. Data Validation Testing

### 3.1 Data Quality Checks

**Test**: Validate generated and processed data

**Transactions Data**:
- [ ] No duplicate transaction IDs
- [ ] All amounts are positive
- [ ] All currencies are valid (BRL, MXN, COP, CLP)
- [ ] All statuses are valid
- [ ] Timestamps are in correct format
- [ ] Provider names are consistent

**Settlements Data**:
- [ ] No duplicate settlement IDs
- [ ] All amounts are positive
- [ ] Settlement dates are after transaction dates
- [ ] All transaction IDs reference valid transactions (except ghosts)

**Reconciled Data**:
- [ ] All transactions present
- [ ] Settlement statuses are logical
- [ ] Expected amounts < transaction amounts
- [ ] Discrepancy calculations are correct
- [ ] Timing anomaly flags are accurate

**Validation Queries** (using Python or SQL):
```python
import pandas as pd

# Check for duplicates
txn_df = pd.read_csv('data/raw/transactions.csv')
assert txn_df['transaction_id'].duplicated().sum() == 0

# Check positive amounts
assert (txn_df['amount'] > 0).all()

# Check valid currencies
assert txn_df['currency'].isin(['BRL', 'MXN', 'COP', 'CLP']).all()
```

---

### 3.2 Fee Calculation Validation

**Test**: Manually verify fee calculations

**Sample Calculations**:

Credit Card (100 BRL):
- [ ] Fee = 100 * 0.029 + 0.30 = 3.20
- [ ] Expected settlement = 100 - 3.20 = 96.80

Bank Transfer (1000 MXN):
- [ ] Fee = 1000 * 0.015 = 15.00
- [ ] Expected settlement = 1000 - 15.00 = 985.00

Cash Voucher (500 CLP):
- [ ] Fee = 500 * 0.035 = 17.50
- [ ] Expected settlement = 500 - 17.50 = 482.50

**Verification Method**:
- [ ] Select sample transactions from reconciled data
- [ ] Calculate expected amounts manually
- [ ] Compare with pipeline output
- [ ] All calculations match

---

### 3.3 Anomaly Detection Validation

**Test**: Verify anomaly detection logic

**Missing Settlements**:
- [ ] All captured transactions without settlements are flagged
- [ ] Authorized-only transactions are NOT flagged
- [ ] Declined transactions are NOT flagged

**Timing Anomalies**:
- [ ] Credit card settlements > 5 days are flagged
- [ ] Bank transfers > 10 days are flagged
- [ ] Cash vouchers > 8 days are flagged

**Ghost Settlements**:
- [ ] Settlements without matching transactions are identified
- [ ] Count matches manual inspection

**Fee Discrepancies**:
- [ ] Settlements differing > 1% or $1 are flagged
- [ ] Small rounding differences are ignored

---

## 4. End-to-End Workflow Testing

### 4.1 Fresh Install Test

**Test**: Simulate fresh installation

```bash
# In a new terminal/directory
git clone <repo-url>
cd horizon-gaming-detector
pip install -r requirements.txt
cd dashboard && npm install
```

**Expected Results**:
- [ ] Repository clones successfully
- [ ] Python dependencies install without errors
- [ ] Node dependencies install without errors
- [ ] No missing dependencies

---

### 4.2 Complete Workflow Execution

**Test**: Run complete workflow from scratch

```bash
# Generate data
python pipeline/generate_data.py

# Run pipeline
python pipeline/main.py

# Start dashboard
cd dashboard
npm run dev
```

**Expected Results**:
- [ ] All steps complete successfully
- [ ] Data flows through entire pipeline
- [ ] Dashboard displays results
- [ ] No errors at any stage

---

### 4.3 Re-run Safety Test

**Test**: Verify pipeline can be re-run safely

```bash
# Run pipeline again
python pipeline/main.py
```

**Expected Results**:
- [ ] Pipeline executes without errors
- [ ] Output files are overwritten
- [ ] No duplicate data created
- [ ] Results are consistent

---

## 5. Error Handling Testing

### 5.1 Missing Files

**Test**: Remove input files and verify error handling

```bash
# Temporarily move data files
mv data/raw/transactions.csv data/raw/transactions.csv.bak
python pipeline/main.py
```

**Expected Results**:
- [ ] Pipeline detects missing file
- [ ] Clear error message displayed
- [ ] Pipeline exits gracefully
- [ ] No corrupted output files created

**Restore**:
```bash
mv data/raw/transactions.csv.bak data/raw/transactions.csv
```

---

### 5.2 Invalid Data

**Test**: Introduce invalid data

Create a test file with:
- Missing required columns
- Invalid currency codes
- Negative amounts
- Invalid date formats

**Expected Results**:
- [ ] Pipeline detects invalid data
- [ ] Error message identifies issue
- [ ] Pipeline exits gracefully

---

### 5.3 Empty Data

**Test**: Test with empty input files

**Expected Results**:
- [ ] Pipeline handles empty files gracefully
- [ ] No division by zero errors
- [ ] Appropriate warning messages
- [ ] Output files created (may be empty)

---

## 6. Performance Testing

### 6.1 Pipeline Performance

**Test**: Measure pipeline execution time

```bash
time python pipeline/main.py
```

**Expected Results**:
- [ ] Pipeline completes in < 30 seconds for 1000 transactions
- [ ] Memory usage is reasonable (< 500 MB)
- [ ] No performance degradation on re-runs

---

### 6.2 Dashboard Performance

**Test**: Measure dashboard load time

**Expected Results**:
- [ ] Initial page load < 3 seconds
- [ ] Charts render in < 1 second
- [ ] Filters respond immediately
- [ ] No lag when interacting with components

---

## 7. Documentation Testing

### 7.1 README Accuracy

**Test**: Follow README instructions exactly

**Expected Results**:
- [ ] All setup steps are accurate
- [ ] All commands work as documented
- [ ] Examples match actual behavior
- [ ] Screenshots match current UI (if present)

---

### 7.2 Code Documentation

**Test**: Verify code documentation

**Expected Results**:
- [ ] All functions have docstrings
- [ ] Docstrings explain parameters and return values
- [ ] Examples in docstrings work
- [ ] Comments explain complex logic

---

## 8. Sign-Off Checklist

### Final Validation

- [ ] All automated tests pass
- [ ] All manual tests completed successfully
- [ ] No critical bugs remaining
- [ ] Documentation is complete and accurate
- [ ] Performance is acceptable
- [ ] Error handling is robust
- [ ] Code quality is professional
- [ ] All acceptance criteria met

### Test Summary

**Date**: _______________
**Tester**: _______________
**Version**: _______________

**Overall Status**: [ ] PASS  [ ] FAIL

**Critical Issues**: _____________________________________

**Notes**: _____________________________________________

---

## Appendix: Common Issues and Solutions

### Issue 1: Module Not Found
**Symptom**: `ModuleNotFoundError: No module named 'pandas'`
**Solution**: `pip install -r requirements.txt`

### Issue 2: Port Already in Use
**Symptom**: `Error: listen EADDRINUSE: address already in use :::3000`
**Solution**: Kill process on port 3000 or use different port

### Issue 3: File Not Found
**Symptom**: `FileNotFoundError: [Errno 2] No such file or directory`
**Solution**: Verify `.env` paths are correct, run from project root

### Issue 4: Empty Output
**Symptom**: Output files are empty or have no data
**Solution**: Check that input data exists and is valid

### Issue 5: Dashboard Not Loading Data
**Symptom**: Dashboard shows "No data" or errors
**Solution**: Verify output JSON files exist and have correct format

---

**End of Manual Testing Checklist**
