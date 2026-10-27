import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"e:\My\the20\test_strategy\commodity source\commodity_equilibrium")

def build_source_registry():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources = [
        # Silver Sources
        {
            "source_id": "SRC_SILVER_INSTITUTE_WSS",
            "metal": "Silver",
            "data_category": "Physical Supply & Demand",
            "source_name": "Silver Institute - World Silver Survey",
            "source_url": "https://silverinstitute.org/all-world-silver-surveys-2025/",
            "data_owner": "The Silver Institute / Metals Focus",
            "source_type": "Industry association",
            "coverage_start": "1990-01-01",
            "coverage_end": "2026-12-31",
            "frequency": "Annual",
            "format": "PDF / HTML",
            "access_method": "HTTPS GET",
            "access_restriction": "Public open access",
            "license_or_terms": "Open for research with citation",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Comprehensive annual global balance: mine supply, scrap, industrial, PV solar, jewelry, coins, market balance"
        },
        {
            "source_id": "SRC_USGS_SILVER_MCS",
            "metal": "Silver",
            "data_category": "Mine Supply & World Reserves",
            "source_name": "USGS Mineral Commodity Summaries: Silver",
            "source_url": "https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-silver.pdf",
            "data_owner": "United States Geological Survey",
            "source_type": "Primary official source",
            "coverage_start": "1996-01-01",
            "coverage_end": "2025-01-01",
            "frequency": "Annual",
            "format": "PDF / Text",
            "access_method": "HTTPS GET",
            "access_restriction": "Public domain (US Gov)",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "US and world mine production by country, reserves, consumption trends"
        },
        {
            "source_id": "SRC_CME_SILVER_FUTURES",
            "metal": "Silver",
            "data_category": "Futures Market & Price",
            "source_name": "COMEX Silver Futures (SI=F)",
            "source_url": "https://finance.yahoo.com/quote/SI=F",
            "data_owner": "CME Group / COMEX via Yahoo Finance",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-08-30",
            "coverage_end": "2026-10-20",
            "frequency": "Daily",
            "format": "Parquet / CSV",
            "access_method": "API / yfinance",
            "access_restriction": "Public API",
            "license_or_terms": "Terms of Service",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Daily OHLCV, volume, continuous contract"
        },
        {
            "source_id": "SRC_CFTC_SILVER_COT",
            "metal": "Silver",
            "data_category": "Positioning",
            "source_name": "CFTC Commitments of Traders: COMEX Silver (084691)",
            "source_url": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm",
            "data_owner": "Commodity Futures Trading Commission",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-01-01",
            "coverage_end": "2026-10-15",
            "frequency": "Weekly",
            "format": "ZIP / CSV / TXT",
            "access_method": "HTTPS GET (Session headers)",
            "access_restriction": "Public regulatory data",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Disaggregated and legacy reports: Commercial, Non-commercial, Managed Money long/short/spreads"
        },
        # Copper Sources
        {
            "source_id": "SRC_ICSG_COPPER_STATS",
            "metal": "Copper",
            "data_category": "Physical Supply & Demand",
            "source_name": "International Copper Study Group - Selected Statistics",
            "source_url": "https://icsg.org/selected-copper-statistics/",
            "data_owner": "International Copper Study Group (ICSG)",
            "source_type": "Industry association",
            "coverage_start": "2010-01-01",
            "coverage_end": "2026-06-30",
            "frequency": "Monthly / Annual",
            "format": "PDF / Excel",
            "access_method": "HTTPS GET",
            "access_restriction": "Public selected tables / Subscription for full DB",
            "license_or_terms": "Fair use with attribution",
            "estimated_cost": "0 USD (Free tier) / Full Yearbook requires membership",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "World refined copper production, usage trends, apparent consumption, warehouse stocks"
        },
        {
            "source_id": "SRC_USGS_COPPER_MCS",
            "metal": "Copper",
            "data_category": "Mine Supply & World Reserves",
            "source_name": "USGS Mineral Commodity Summaries: Copper",
            "source_url": "https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-copper.pdf",
            "data_owner": "United States Geological Survey",
            "source_type": "Primary official source",
            "coverage_start": "1996-01-01",
            "coverage_end": "2025-01-01",
            "frequency": "Annual",
            "format": "PDF / Text",
            "access_method": "HTTPS GET",
            "access_restriction": "Public domain (US Gov)",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "World mine production (Chile, Peru, China, DRC), refinery production, reserves"
        },
        {
            "source_id": "SRC_CME_COPPER_FUTURES",
            "metal": "Copper",
            "data_category": "Futures Market & Price",
            "source_name": "COMEX Copper Futures (HG=F)",
            "source_url": "https://finance.yahoo.com/quote/HG=F",
            "data_owner": "CME Group / COMEX via Yahoo Finance",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-08-30",
            "coverage_end": "2026-10-20",
            "frequency": "Daily",
            "format": "Parquet / CSV",
            "access_method": "API / yfinance",
            "access_restriction": "Public API",
            "license_or_terms": "Terms of Service",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Daily OHLCV, volume, continuous contract"
        },
        {
            "source_id": "SRC_CFTC_COPPER_COT",
            "metal": "Copper",
            "data_category": "Positioning",
            "source_name": "CFTC Commitments of Traders: COMEX Copper (085692)",
            "source_url": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm",
            "data_owner": "Commodity Futures Trading Commission",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-01-01",
            "coverage_end": "2026-10-15",
            "frequency": "Weekly",
            "format": "ZIP / CSV / TXT",
            "access_method": "HTTPS GET (Session headers)",
            "access_restriction": "Public regulatory data",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Disaggregated and legacy reports: Managed money, commercial, non-commercial positions"
        },
        # Platinum Sources
        {
            "source_id": "SRC_WPIC_PLATINUM_HISTORIC",
            "metal": "Platinum",
            "data_category": "Physical Supply & Demand",
            "source_name": "World Platinum Investment Council - Platinum Quarterly & Historic Database",
            "source_url": "https://platinuminvestment.com/supply-and-demand/historic-data",
            "data_owner": "World Platinum Investment Council (WPIC) / Metals Focus / SFA Oxford",
            "source_type": "Industry association",
            "coverage_start": "1975-01-01",
            "coverage_end": "2026-06-30",
            "frequency": "Quarterly / Annual",
            "format": "Excel (XLSX / XLS)",
            "access_method": "HTTPS GET",
            "access_restriction": "Public open access",
            "license_or_terms": "Free for download with citation",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Comprehensive quarterly and annual balance from 1975 to 2026: mining (SA, Russia, Zim), autocatalyst, industrial, jewelry, ETF, total balance"
        },
        {
            "source_id": "SRC_USGS_PLATINUM_MCS",
            "metal": "Platinum",
            "data_category": "Mine Supply & World Reserves",
            "source_name": "USGS Mineral Commodity Summaries: Platinum-Group Metals",
            "source_url": "https://pubs.usgs.gov/periodicals/mcs2022/mcs2022-platinum.pdf",
            "data_owner": "United States Geological Survey",
            "source_type": "Primary official source",
            "coverage_start": "1996-01-01",
            "coverage_end": "2025-01-01",
            "frequency": "Annual",
            "format": "PDF / Text",
            "access_method": "HTTPS GET",
            "access_restriction": "Public domain",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "US & global mine production of platinum and palladium, recycling, reserves"
        },
        {
            "source_id": "SRC_NYMEX_PLATINUM_FUTURES",
            "metal": "Platinum",
            "data_category": "Futures Market & Price",
            "source_name": "NYMEX Platinum Futures (PL=F)",
            "source_url": "https://finance.yahoo.com/quote/PL=F",
            "data_owner": "CME Group / NYMEX via Yahoo Finance",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-01-04",
            "coverage_end": "2026-10-20",
            "frequency": "Daily",
            "format": "Parquet / CSV",
            "access_method": "API / yfinance",
            "access_restriction": "Public API",
            "license_or_terms": "Terms of Service",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Daily OHLCV, volume, continuous contract"
        },
        {
            "source_id": "SRC_CFTC_PLATINUM_COT",
            "metal": "Platinum",
            "data_category": "Positioning",
            "source_name": "CFTC Commitments of Traders: NYMEX Platinum (076651)",
            "source_url": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm",
            "data_owner": "Commodity Futures Trading Commission",
            "source_type": "Exchange or regulator",
            "coverage_start": "2000-01-01",
            "coverage_end": "2026-10-15",
            "frequency": "Weekly",
            "format": "ZIP / CSV / TXT",
            "access_method": "HTTPS GET (Session headers)",
            "access_restriction": "Public regulatory data",
            "license_or_terms": "Public domain",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Disaggregated and legacy reports: Managed money, commercial, non-commercial positions"
        },
        # Common / Macro Sources
        {
            "source_id": "SRC_WORLD_BANK_PINKSHEET",
            "metal": "Common / Multi-metal",
            "data_category": "Global Benchmark Prices",
            "source_name": "World Bank Commodity Markets Pink Sheet",
            "source_url": "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx",
            "data_owner": "The World Bank Group",
            "source_type": "Licensed data provider / Intergovernmental",
            "coverage_start": "1960-01-01",
            "coverage_end": "2026-09-30",
            "frequency": "Monthly",
            "format": "Excel (XLSX)",
            "access_method": "HTTPS GET",
            "access_restriction": "Public open data",
            "license_or_terms": "CC BY 4.0",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "Global monthly benchmark spot prices for Silver, Copper, Platinum, Gold, Crude Oil, Aluminum"
        },
        {
            "source_id": "SRC_FRED_MACRO_FACTORS",
            "metal": "Macro / Cross-market",
            "data_category": "Macro & Cross-market Variables",
            "source_name": "Federal Reserve Economic Data (FRED)",
            "source_url": "https://fred.stlouisfed.org/",
            "data_owner": "Federal Reserve Bank of St. Louis",
            "source_type": "Primary official source",
            "coverage_start": "1962-01-02",
            "coverage_end": "2026-10-19",
            "frequency": "Daily / Monthly",
            "format": "CSV",
            "access_method": "Direct CSV endpoint",
            "access_restriction": "Public domain",
            "license_or_terms": "Public data",
            "estimated_cost": "0 USD",
            "last_checked_at": now_str,
            "download_status": "Verified",
            "notes": "US 10Y Real Yield (DFII10), US 10Y Nominal (DGS10), Breakeven Inflation (T10YIE), Broad USD (DTWEXBGS), US IP (INDPRO)"
        }
    ]
    
    df_reg = pd.DataFrame(sources)
    out_csv = BASE_DIR / "01_source_registry" / "source_registry.csv"
    df_reg.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"Built Source Registry with {len(df_reg)} sources -> {out_csv}")
    return df_reg

def build_data_dictionary():
    dict_items = [
        # Silver
        {"metal": "Silver", "metric_name": "mine_production", "metric_category": "Physical Supply", "standard_unit": "Moz", "original_unit": "Moz / Tonnes", "frequency": "Annual", "description": "Global silver mine output", "economic_relationship": "Supply driver. Cost and byproduct dynamics (lead/zinc/copper mines).", "calculation_formula": "Direct reported / Sum of countries"},
        {"metal": "Silver", "metric_name": "recycling_supply", "metric_category": "Physical Supply", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Scrap recovery from industrial and jewelry sources", "economic_relationship": "Price elastic secondary supply.", "calculation_formula": "Direct reported"},
        {"metal": "Silver", "metric_name": "net_hedging_supply", "metric_category": "Physical Supply", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Producer de-hedging or forward sales", "economic_relationship": "Financial supply contribution.", "calculation_formula": "Direct reported"},
        {"metal": "Silver", "metric_name": "total_supply", "metric_category": "Physical Supply", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Aggregate global physical silver supply", "economic_relationship": "Supply curve aggregate.", "calculation_formula": "mine_production + recycling_supply + net_hedging_supply + official_sales"},
        {"metal": "Silver", "metric_name": "industrial_demand", "metric_category": "Physical Demand", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Silver used in electronics, solar PV, brazing, and catalysts", "economic_relationship": "Structural demand growth, high GDP/tech elasticity.", "calculation_formula": "Sum of subsectors"},
        {"metal": "Silver", "metric_name": "photovoltaic_demand", "metric_category": "Physical Demand", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Silver paste consumption in solar panel cells", "economic_relationship": "Clean energy transition driver; key structural deficit engine.", "calculation_formula": "Direct reported (Metals Focus)"},
        {"metal": "Silver", "metric_name": "jewelry_silverware_demand", "metric_category": "Physical Demand", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Jewelry and silverware fabrication", "economic_relationship": "Consumer discretionary, price sensitive.", "calculation_formula": "Direct reported"},
        {"metal": "Silver", "metric_name": "physical_investment_demand", "metric_category": "Physical Demand", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Silver bars and official coins purchased by retail and private investors", "economic_relationship": "Safe haven and inflation hedge demand.", "calculation_formula": "Direct reported"},
        {"metal": "Silver", "metric_name": "total_physical_demand", "metric_category": "Physical Demand", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Total global physical silver consumption", "economic_relationship": "Demand curve aggregate.", "calculation_formula": "industrial_demand + jewelry_silverware_demand + physical_investment_demand"},
        {"metal": "Silver", "metric_name": "market_balance_reported", "metric_category": "Market Balance", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Reported market balance published by Silver Institute", "economic_relationship": "Surplus (+), Deficit (-). Primary physical balance anchor.", "calculation_formula": "Direct from survey"},
        {"metal": "Silver", "metric_name": "market_balance_calculated", "metric_category": "Market Balance", "standard_unit": "Moz", "original_unit": "Moz", "frequency": "Annual", "description": "Calculated physical balance", "economic_relationship": "Surplus (+), Deficit (-).", "calculation_formula": "total_supply - total_physical_demand"},
        
        # Copper
        {"metal": "Copper", "metric_name": "mine_production", "metric_category": "Physical Supply", "standard_unit": "kt", "original_unit": "kt / mt", "frequency": "Annual / Monthly", "description": "Copper concentrate and SX-EW mine production", "economic_relationship": "Primary upstream supply. Key nodes: Chile, Peru, DRC, China.", "calculation_formula": "Direct reported"},
        {"metal": "Copper", "metric_name": "refined_production", "metric_category": "Physical Supply", "standard_unit": "kt", "original_unit": "kt", "frequency": "Annual / Monthly", "description": "Total refined copper output from primary and secondary smelters", "economic_relationship": "Tradable physical cathode supply.", "calculation_formula": "Primary refined + Secondary refined"},
        {"metal": "Copper", "metric_name": "refined_usage", "metric_category": "Physical Demand", "standard_unit": "kt", "original_unit": "kt", "frequency": "Annual / Monthly", "description": "Apparent and estimated refined copper usage/consumption", "economic_relationship": "Global industrial cycle bellwether (Dr. Copper).", "calculation_formula": "Direct reported by ICSG"},
        {"metal": "Copper", "metric_name": "market_balance_reported", "metric_category": "Market Balance", "standard_unit": "kt", "original_unit": "kt", "frequency": "Annual / Monthly", "description": "World refined copper balance (Surplus/Deficit)", "economic_relationship": "Positive = Surplus, Negative = Deficit.", "calculation_formula": "refined_production - refined_usage"},
        {"metal": "Copper", "metric_name": "warehouse_stocks", "metric_category": "Inventory", "standard_unit": "kt", "original_unit": "kt / tonnes", "frequency": "Daily / Weekly", "description": "Exchange warehouse stocks (LME + SHFE + COMEX)", "economic_relationship": "Direct buffer inventory, inversely correlated with spread/backwardation.", "calculation_formula": "LME + SHFE + COMEX"},
        
        # Platinum
        {"metal": "Platinum", "metric_name": "total_mining_supply", "metric_category": "Physical Supply", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Global refined mine supply (South Africa, Russia, Zimbabwe, North America)", "economic_relationship": "Geographically concentrated supply; susceptible to power cuts and strikes.", "calculation_formula": "Direct reported by WPIC"},
        {"metal": "Platinum", "metric_name": "recycling_supply", "metric_category": "Physical Supply", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Secondary supply recovered from autocatalysts, electronics, and jewelry", "economic_relationship": "Vehicle scrap rate and steel cycle dependent.", "calculation_formula": "Autocatalyst scrap + Jewelry scrap + Industrial scrap"},
        {"metal": "Platinum", "metric_name": "total_supply", "metric_category": "Physical Supply", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Total global platinum supply", "economic_relationship": "Total physical inflows.", "calculation_formula": "total_mining_supply + recycling_supply"},
        {"metal": "Platinum", "metric_name": "automotive_demand", "metric_category": "Physical Demand", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Autocatalysts for diesel and heavy-duty hybrid internal combustion engines", "economic_relationship": "Largest single demand segment (~40%). Regulated emissions standards.", "calculation_formula": "Direct reported"},
        {"metal": "Platinum", "metric_name": "industrial_demand", "metric_category": "Physical Demand", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Chemical, petroleum, glass, medical, and hydrogen PEM electrolyzers", "economic_relationship": "Industrial capacity expansion and hydrogen economy.", "calculation_formula": "Sum of chemical, medical, glass, petroleum"},
        {"metal": "Platinum", "metric_name": "jewelry_demand", "metric_category": "Physical Demand", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Jewelry fabrication (primarily China, Japan, India, US)", "economic_relationship": "Luxury demand, substitution with white gold.", "calculation_formula": "Direct reported"},
        {"metal": "Platinum", "metric_name": "investment_demand", "metric_category": "Physical Demand", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Bars, coins, and ETF physical metal holdings change", "economic_relationship": "Financial investor flows.", "calculation_formula": "Bar & coin + ETF change + Exchange stock change"},
        {"metal": "Platinum", "metric_name": "total_demand", "metric_category": "Physical Demand", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Total global platinum demand", "economic_relationship": "Total physical outflows.", "calculation_formula": "automotive + industrial + jewelry + investment"},
        {"metal": "Platinum", "metric_name": "market_balance_reported", "metric_category": "Market Balance", "standard_unit": "koz", "original_unit": "koz", "frequency": "Quarterly / Annual", "description": "Reported market balance published by WPIC", "economic_relationship": "Positive = Surplus, Negative = Deficit.", "calculation_formula": "total_supply - total_demand"}
    ]
    df_dict = pd.DataFrame(dict_items)
    out_csv = BASE_DIR / "01_source_registry" / "data_dictionary.csv"
    df_dict.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"Built Data Dictionary with {len(df_dict)} metrics -> {out_csv}")
    return df_dict

if __name__ == "__main__":
    build_source_registry()
    build_data_dictionary()
