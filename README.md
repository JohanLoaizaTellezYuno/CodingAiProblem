# Horizon Gaming Revenue Anomaly Detector

A comprehensive data analysis pipeline and dashboard for detecting revenue anomalies in gaming transaction data across Latin American payment providers.

## Overview

Horizon Gaming processes payments across multiple Latin American countries (Brazil, Mexico, Colombia, Chile) using various payment methods including credit/debit cards, bank transfers, and cash vouchers. This system analyzes transaction and settlement data to identify discrepancies, timing issues, and potential revenue leaks.

## Features

- **Multi-Currency Support**: Handles BRL, MXN, COP, CLP with automatic USD conversion
- **Payment Method Analysis**: Processes credit cards, debit cards, bank transfers, and cash vouchers
- **Fee Calculation Engine**: Accurate fee calculations based on payment method:
  - Credit/Debit Cards: 2.9% + $0.30 per transaction
  - Bank Transfers: 1.5% of transaction amount
  - Cash Vouchers: 3.5% of transaction amount
- **Settlement Timing Validation**: Flags unusual settlement delays
- **Interactive Dashboard**: Next.js-based visualization interface
- **Automated Testing**: Comprehensive test suite with pytest

## Project Structure

```
horizon-gaming-detector/
├── dashboard/              # Next.js dashboard application
│   ├── app/               # Next.js app router pages
│   ├── components/        # React components
│   ├── lib/               # Utility libraries
│   ├── public/            # Static assets
│   └── types/             # TypeScript type definitions
├── pipeline/              # Python data processing pipeline
│   ├── config.py          # Configuration management
│   ├── fees.py            # Fee calculation logic
│   ├── generate_data.py   # Test data generation
│   └── validate_data.py   # Data validation utilities
├── data/                  # Data directory (gitignored)
│   ├── raw/               # Raw transaction and settlement data
│   └── processed/         # Processed analysis results
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── .env.example           # Environment variable template
└── requirements.txt       # Python dependencies
```

## Installation

### Python Pipeline Setup

1. Clone the repository:
```bash
git clone https://github.com/JohanLoaizaTellezYuno/CodingAiProblem.git
cd horizon-gaming-detector
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Dashboard Setup

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Running the Pipeline

```python
from pipeline.config import Config
from pipeline.fees import calculate_fee, convert_to_usd

# Calculate processing fee
fee = calculate_fee(100.0, 'credit_card')

# Convert currency
usd_amount = convert_to_usd(500.0, 'BRL')
```

### Running Tests

```bash
pytest
pytest --cov  # With coverage report
```

## Technology Stack

**Backend Pipeline:**
- Python 3.8+
- pandas (data manipulation)
- numpy (numerical operations)
- python-dotenv (configuration management)
- pytest (testing)

**Frontend Dashboard:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS

## Configuration

Key configuration parameters in `.env`:

- **Data Paths**: Locations of transaction and settlement data files
- **Fee Parameters**: Processing fee percentages and fixed fees
- **Exchange Rates**: Currency conversion rates to USD
- **Settlement Timing**: Expected settlement timeframes by payment method

## Recent Changes

### [2026-02-25] - Add pipeline configuration and fee calculation modules
- Added `pipeline/config.py` for centralized configuration management
- Implemented `pipeline/fees.py` with fee calculation logic for all payment methods
- Added Next.js dashboard with initial setup and structure
- Configured multi-currency support for BRL, MXN, COP, CLP
- Set up settlement timing validation parameters

## Contributing

This is a private repository for Horizon Gaming. For internal contributions:

1. Create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Ensure all tests pass
4. Submit a pull request for review

## License

Proprietary - Horizon Gaming Internal Use Only
