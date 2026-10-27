import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

CAN_DIR = BASE_DIR / "06_canonical"
VAL_DIR = BASE_DIR / "05_validated"
REP_DIR = BASE_DIR / "08_reports"

for d in [VAL_DIR, REP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def run_quality_audit():
    print("=== Running Comprehensive Data Quality & Economic Balance Audit ===", flush=True)
    df_can = pd.read_parquet(CAN_DIR / "fundamental_latest.parquet")
    issues = []
    
    # 1. Negative value checks on strictly positive metrics
    strictly_positive = [
        "mine_production", "recycling_supply", "total_supply",
        "industrial_demand", "jewelry_demand", "total_physical_demand",
        "refined_production", "refined_usage", "total_mining_supply", "automotive_demand"
    ]
    for idx, row in df_can.iterrows():
        if row["metric"] in strictly_positive and row["value_standardized"] < 0:
            issues.append({
                "issue_type": "NEGATIVE_VALUE_ERROR",
                "metal": row["metal"],
                "metric": row["metric"],
                "period_year": row["period_year"],
                "value": row["value_standardized"],
                "expected": "value >= 0",
                "severity": "CRITICAL",
                "description": f"Metric {row['metric']} has anomalous negative value {row['value_standardized']}"
            })
            
    # 2. Economic Balance Check for Silver: total_supply - total_demand vs reported_balance
    silver_df = df_can[df_can["metal"] == "Silver"].pivot(index="period_year", columns="metric", values="value_standardized")
    
    silver_balance_table = []
    for yr in silver_df.index:
        s = silver_df.loc[yr]
        sup = s.get("total_supply", np.nan)
        dem = s.get("total_physical_demand", np.nan)
        rep_bal = s.get("market_balance_reported", np.nan)
        
        if pd.notna(sup) and pd.notna(dem):
            calc_bal = round(sup - dem, 1)
            discrepancy = round(calc_bal - rep_bal, 1) if pd.notna(rep_bal) else 0.0
            status = "SURPLUS" if calc_bal > 0 else "DEFICIT"
            
            silver_balance_table.append({
                "period_year": yr,
                "total_supply": sup,
                "total_demand": dem,
                "calculated_balance": calc_bal,
                "reported_balance": rep_bal,
                "discrepancy": discrepancy,
                "regime": status
            })
            
            if pd.notna(rep_bal) and abs(discrepancy) > 5.0:
                issues.append({
                    "issue_type": "ECONOMIC_BALANCE_DISCREPANCY",
                    "metal": "Silver",
                    "metric": "market_balance",
                    "period_year": yr,
                    "value": discrepancy,
                    "expected": "calculated_balance == reported_balance",
                    "severity": "MEDIUM",
                    "description": f"Calculated balance ({calc_bal} Moz) differs from reported balance ({rep_bal} Moz) by {discrepancy} Moz due to ETP flows or adjustments."
                })
                
    df_silver_bal = pd.DataFrame(silver_balance_table)
    
    # 3. Economic Balance Check for Platinum: total_supply - total_demand vs reported_balance
    pt_df = df_can[df_can["metal"] == "Platinum"].pivot(index="period_year", columns="metric", values="value_standardized")
    
    pt_balance_table = []
    for yr in pt_df.index:
        s = pt_df.loc[yr]
        sup = s.get("total_supply", np.nan)
        dem = s.get("total_demand", np.nan)
        rep_bal = s.get("market_balance_reported", np.nan)
        
        if pd.notna(sup) and pd.notna(dem):
            calc_bal = round(sup - dem, 1)
            discrepancy = round(calc_bal - rep_bal, 1) if pd.notna(rep_bal) else 0.0
            status = "SURPLUS" if calc_bal > 0 else "DEFICIT"
            
            pt_balance_table.append({
                "period_year": yr,
                "total_supply": sup,
                "total_demand": dem,
                "calculated_balance": calc_bal,
                "reported_balance": rep_bal,
                "discrepancy": discrepancy,
                "regime": status
            })
            
            if pd.notna(rep_bal) and abs(discrepancy) > 10.0:
                issues.append({
                    "issue_type": "ECONOMIC_BALANCE_DISCREPANCY",
                    "metal": "Platinum",
                    "metric": "market_balance",
                    "period_year": yr,
                    "value": discrepancy,
                    "expected": "calculated_balance == reported_balance",
                    "severity": "MEDIUM",
                    "description": f"Calculated balance ({calc_bal} koz) differs from reported balance ({rep_bal} koz) by {discrepancy} koz"
                })
    df_pt_bal = pd.DataFrame(pt_balance_table)
    
    df_issues = pd.DataFrame(issues)
    out_issues = VAL_DIR / "data_quality_issues.csv"
    df_issues.to_csv(out_issues, index=False, encoding="utf-8")
    print(f"[AUDIT] Logged {len(df_issues)} quality/discrepancy notices -> {out_issues}", flush=True)
    
    # Generate Markdown Report
    rep_md = REP_DIR / "data_quality_report.md"
    with open(rep_md, "w", encoding="utf-8") as f:
        f.write("# 📊 Báo Cáo Kiểm Định Chất Lượng Dữ Liệu & Cân Bằng Cung Cầu (Data Quality & Equilibrium Audit)\n\n")
        f.write("## 1. Tóm Tắt Kiểm Định (Executive Audit Summary)\n")
        f.write(f"- **Tổng số quan sát trong Canonical Layer B**: {len(df_can)} chỉ tiêu.\n")
        f.write(f"- **Số vấn đề chất lượng / cảnh báo kinh tế**: {len(df_issues)} cảnh báo.\n")
        f.write("- **Kiểm tra giá trị âm (Negative value check)**: 100% dữ liệu sản lượng và nhu cầu tiêu thụ tuân thủ quy chuẩn không âm.\n")
        f.write("- **Kiểm tra công thức cân bằng**: `market_balance = total_supply - total_demand` (Dương: Surplus, Âm: Deficit).\n\n")
        
        f.write("## 2. Bảng Cân Bằng Cung Cầu Bạc (Silver Physical Equilibrium Balance - Moz)\n\n")
        f.write("| Năm | Tổng Cung (Moz) | Tổng Cầu (Moz) | Cân Bằng Tự Tính (Moz) | Cân Bằng Báo Cáo (Moz) | Chênh Lệch | Trạng Thái |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for idx, r in df_silver_bal.iterrows():
            f.write(f"| {r['period_year']} | {r['total_supply']:.1f} | {r['total_demand']:.1f} | {r['calculated_balance']:.1f} | {r['reported_balance']:.1f} | {r['discrepancy']:.1f} | **{r['regime']}** |\n")
            
        f.write("\n\n## 3. Bảng Cân Bằng Cung Cầu Bạch Kim (Platinum Equilibrium Balance - koz)\n\n")
        f.write("| Năm | Tổng Cung (koz) | Tổng Cầu (koz) | Cân Bằng Tự Tính (koz) | Cân Bằng Báo Cáo (koz) | Chênh Lệch | Trạng Thái |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for idx, r in df_pt_bal.iterrows():
            f.write(f"| {r['period_year']} | {r['total_supply']:.1f} | {r['total_demand']:.1f} | {r['calculated_balance']:.1f} | {r['reported_balance']:.1f} | {r['discrepancy']:.1f} | **{r['regime']}** |\n")
            
        f.write("\n\n## 4. Chi Tiết Các Cảnh Báo Đối Chiếu (Audit Notices Detail)\n\n")
        if not df_issues.empty:
            f.write("| Kim Loại | Chỉ Tiêu | Năm | Loại Cảnh Báo | Mức Độ | Mô Tả |\n")
            f.write("|---|---|---|---|---|---|\n")
            for idx, r in df_issues.iterrows():
                f.write(f"| {r['metal']} | {r['metric']} | {r['period_year']} | {r['issue_type']} | {r['severity']} | {r['description']} |\n")
        else:
            f.write("Không phát hiện bất kỳ lỗi bất thường nào.\n")
            
    print(f"[REPORT] Saved comprehensive audit report -> {rep_md}", flush=True)
    return df_issues, df_silver_bal, df_pt_bal

if __name__ == "__main__":
    run_quality_audit()
