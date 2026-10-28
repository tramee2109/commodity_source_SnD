"""
Master CLI Ingestion Orchestrator for ACM Nano Metals Platform.
Runs all or selected pipelines with checkpoint management, deduplication, and status monitoring.

Usage:
  python run_sync.py              # Run all pipelines incrementally (skips existing dates)
  python run_sync.py --status     # View current watermarks without syncing
  python run_sync.py --acm        # Sync only ACM Nano exchange data
  python run_sync.py --benchmarks # Sync only COMEX/NYMEX futures and miners
  python run_sync.py --cot        # Sync only CFTC COT positioning
  python run_sync.py --force      # Force full re-download ignoring checkpoints
"""

import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.checkpoint import CheckpointManager
from pipelines.acm_loader import run_acm_pipeline
from pipelines.benchmark_loader import run_benchmark_pipeline
from pipelines.cot_loader import run_cot_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def show_dashboard():
    """Display current watermarks and record counts."""
    chk_mgr = CheckpointManager()
    rows = chk_mgr.get_all_checkpoints()

    print("\n" + "=" * 92)
    print("                ACM NANO METALS PLATFORM: INGESTION CHECKPOINT DASHBOARD")
    print("=" * 92)
    print(f"{'Pipeline':<28} | {'Entity':<12} | {'Watermark (Data Date)':<22} | {'Records':<8} | {'Status'}")
    print("-" * 92)

    if not rows:
        print("  No checkpoints recorded yet. Run 'python run_sync.py' to perform initial ingestion.")
    else:
        for r in rows:
            pipe, entity, last_sync, data_ts, count, status, err = r
            dt_display = str(data_ts).split()[0] if data_ts else "None"
            status_tag = "[OK] SUCCESS" if status == "SUCCESS" else f"[!] {status}"
            print(f"{pipe:<28} | {entity:<12} | {dt_display:<22} | {count:<8} | {status_tag}")
    print("=" * 92 + "\n")

def main():
    parser = argparse.ArgumentParser(description="ACM Nano Metals Data Ingestion Orchestrator")
    parser.add_argument("--status", action="store_true", help="Display watermark dashboard only")
    parser.add_argument("--acm", action="store_true", help="Sync ACM Nano Metals only")
    parser.add_argument("--benchmarks", action="store_true", help="Sync Benchmark futures and miners only")
    parser.add_argument("--cot", action="store_true", help="Sync CFTC COT positioning only")
    parser.add_argument("--force", action="store_true", help="Force re-sync ignoring existing watermarks")

    args = parser.parse_args()

    if args.status:
        show_dashboard()
        return

    print("==========================================================================")
    print(f"[*] ACM NANO METALS SYNC STARTED AT {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("==========================================================================")

    run_all = not (args.acm or args.benchmarks or args.cot)

    # 1. ACM Exchange
    if run_all or args.acm:
        try:
            run_acm_pipeline(force=args.force)
        except Exception as e:
            logging.error(f"ACM pipeline error: {e}")

    # 2. Benchmark Futures & Miners
    if run_all or args.benchmarks:
        try:
            run_benchmark_pipeline(force_full=args.force)
        except Exception as e:
            logging.error(f"Benchmark pipeline error: {e}")

    # 3. CFTC COT Positioning
    if run_all or args.cot:
        try:
            run_cot_pipeline()
        except Exception as e:
            logging.error(f"CFTC COT pipeline error: {e}")

    # Final Dashboard
    show_dashboard()

if __name__ == "__main__":
    main()
