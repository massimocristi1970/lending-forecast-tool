# Lending Forecast Tool

A comprehensive Streamlit-based financial modeling tool for lending businesses that provides forecasting, unit economics analysis, and scenario comparison capabilities.

## Features

- **Monthly Lending Volume Forecasting**: Project lending volumes with configurable growth rates
- **Unit Economics Analysis**: Calculate revenue, costs, and profitability per loan
- **Bad Debt Modeling**: Factor in default rates and recovery scenarios
- **Scenario Comparison**: Save and compare multiple business scenarios
- **Interactive Visualizations**: Charts showing trends and cashflow projections
- **Excel Export**: Download complete forecast data as Excel files

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. **Clone or download this repository**
   ```bash
   cd C:\Dev\GitHub
   git clone <your-repo-url>  # or download and extract
   cd lending-forecast-tool
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Activate virtual environment** (if not already active)
   ```bash
   venv\Scripts\activate
   ```

2. **Run the application**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to `http://localhost:8501`

## Configuration

### Key Parameters
- **Lending Volume**: Starting monthly lending amount
- **Growth Rate**: Monthly compound growth percentage
- **Loan Terms**: Duration and size parameters
- **Costs**: Acquisition costs and operational expenses
- **Risk Parameters**: Bad debt rates and recovery assumptions

### Advanced Settings
- Fixed operating costs
- Variable cost percentages
- Revenue scaling factors

## Output

The tool generates:
- Monthly forecast tables with key metrics
- Trend charts showing revenue, costs, and profitability
- Cashflow projections with repayment timing
- Scenario comparison analysis
- Downloadable Excel reports

## Business Logic

- Revenue scales based on loan amount and term relative to £300/3-month baseline
- Repayment flow assumes straight-line amortization
- Net cashflow includes all fixed and variable costs
- Bad debt provision calculated upfront with configurable recovery rates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Built with Streamlit** 🚀