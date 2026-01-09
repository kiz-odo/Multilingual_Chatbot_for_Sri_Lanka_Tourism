#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Coverage Verification Script
Verifies actual test coverage percentage and generates report
"""

import subprocess
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def run_coverage_check():
    """Run pytest with coverage and generate report"""
    print("=" * 60)
    print("Test Coverage Verification")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(backend_path)
    
    try:
        # Run pytest with coverage
        print("\nRunning tests with coverage...")
        result = subprocess.run(
            [
                "python", "-m", "pytest",
                "tests/",
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=json:coverage.json",
                "-v"
            ],
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # Check if coverage.json exists and parse it
        coverage_file = backend_path / "coverage.json"
        if coverage_file.exists():
            import json
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
            
            print("\n" + "=" * 60)
            print("Coverage Results")
            print("=" * 60)
            print(f"Total Coverage: {total_coverage:.2f}%")
            print(f"Target Coverage: 85.00%")
            
            if total_coverage >= 85:
                print("[PASS] Coverage target met!")
            else:
                print(f"[WARN] Coverage below target by {85 - total_coverage:.2f}%")
            
            # Show per-file coverage
            print("\nPer-File Coverage:")
            print("-" * 60)
            files = coverage_data.get("files", {})
            sorted_files = sorted(files.items(), key=lambda x: x[1].get("summary", {}).get("percent_covered", 0))
            
            for file_path, file_data in sorted_files:
                file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
                rel_path = file_path.replace(str(backend_path) + "/", "")
                status = "[PASS]" if file_coverage >= 80 else "[WARN]" if file_coverage >= 50 else "[FAIL]"
                print(f"{status} {rel_path}: {file_coverage:.1f}%")
            
            print("\nHTML Report generated at: backend/htmlcov/index.html")
            print("JSON Report generated at: backend/coverage.json")
            
            return {
                "success": True,
                "coverage": total_coverage,
                "target_met": total_coverage >= 85
            }
        else:
            print("[WARN] Coverage report not generated")
            return {
                "success": False,
                "coverage": 0,
                "target_met": False
            }
            
    except FileNotFoundError:
        print("[ERROR] pytest or pytest-cov not installed")
        print("Install with: pip install pytest pytest-cov")
        return {
            "success": False,
            "coverage": 0,
            "target_met": False
        }
    except Exception as e:
        print(f"[ERROR] Error running coverage: {e}")
        return {
            "success": False,
            "coverage": 0,
            "target_met": False
        }


def generate_coverage_summary():
    """Generate a summary markdown file"""
    coverage_file = backend_path / "coverage.json"
    
    if not coverage_file.exists():
        print("[WARN] Coverage file not found. Run tests first.")
        return
    
    import json
    with open(coverage_file, 'r') as f:
        coverage_data = json.load(f)
    
    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
    
    summary = f"""# Test Coverage Report

**Generated:** {Path(__file__).stat().st_mtime}

## Summary

- **Total Coverage:** {total_coverage:.2f}%
- **Target Coverage:** 85.00%
- **Status:** {"✅ Target Met" if total_coverage >= 85 else "⚠️ Below Target"}

## Coverage Breakdown

"""
    
    files = coverage_data.get("files", {})
    sorted_files = sorted(files.items(), key=lambda x: x[1].get("summary", {}).get("percent_covered", 0), reverse=True)
    
    summary += "| File | Coverage | Status |\n"
    summary += "|------|----------|--------|\n"
    
    for file_path, file_data in sorted_files:
        file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
        rel_path = file_path.replace(str(backend_path) + "/", "")
        status = "PASS" if file_coverage >= 80 else "WARN" if file_coverage >= 50 else "FAIL"
        summary += f"| `{rel_path}` | {file_coverage:.1f}% | {status} |\n"
    
    summary_file = backend_path / "COVERAGE_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\nCoverage summary saved to: {summary_file}")


if __name__ == "__main__":
    result = run_coverage_check()
    
    if result["success"]:
        generate_coverage_summary()
    
    # Exit with appropriate code
    sys.exit(0 if result["target_met"] else 1)

