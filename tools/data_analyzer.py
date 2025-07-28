#!/usr/bin/env python3
"""
Data Analysis Tool for GenXData

This tool provides comprehensive analysis of CSV data including:
- Basic statistics (rows, columns, missing values)
- Descriptive statistics for numeric columns
- Frequency analysis for categorical columns
- Distribution visualizations
- Correlation analysis
- Data quality assessment

Usage:
    python tools/data_analyzer.py input.csv
    python tools/data_analyzer.py input.csv --output-dir analysis_results
    python tools/data_analyzer.py input.csv --format html
"""

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Set matplotlib backend for headless environments
plt.switch_backend("Agg")

# Set style for better-looking plots
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


class DataAnalyzer:
    """Comprehensive data analysis tool for CSV files."""

    def __init__(self, csv_path: str, output_dir: str = "analysis_output"):
        """
        Initialize the data analyzer.

        Args:
            csv_path: Path to the CSV file to analyze
            output_dir: Directory to save analysis results
        """
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories for different types of outputs
        (self.output_dir / "plots").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)

        self.df = None
        self.analysis_results = {}

    def load_data(self) -> pd.DataFrame:
        """Load CSV data with error handling."""
        try:
            print(f"📊 Loading data from {self.csv_path}")
            self.df = pd.read_csv(self.csv_path)
            print(
                f"✅ Successfully loaded {len(self.df)} rows and "
                f"{len(self.df.columns)} columns"
            )
            return self.df
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            sys.exit(1)

    def basic_info(self) -> dict[str, Any]:
        """Generate basic dataset information."""
        print("\n📋 Analyzing basic dataset information...")

        info = {
            "filename": self.csv_path.name,
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "memory_usage_mb": round(
                self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2
            ),
            "columns": list(self.df.columns),
            "data_types": self.df.dtypes.astype(str).to_dict(),
        }

        # Missing values analysis
        missing_values = self.df.isnull().sum()
        missing_percentages = (missing_values / len(self.df) * 100).round(2)

        info["missing_values"] = {
            "counts": missing_values.to_dict(),
            "percentages": missing_percentages.to_dict(),
            "total_missing": int(missing_values.sum()),
            "columns_with_missing": missing_values[missing_values > 0].index.tolist(),
        }

        self.analysis_results["basic_info"] = info
        return info

    def analyze_numeric_columns(self) -> dict[str, dict[str, Any]]:
        """Analyze numeric columns with descriptive statistics."""
        print("\n🔢 Analyzing numeric columns...")

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        numeric_analysis = {}

        for col in numeric_cols:
            print(f"  📊 Analyzing {col}")
            series = self.df[col].dropna()

            if len(series) == 0:
                numeric_analysis[col] = {"error": "No non-null values"}
                continue

            analysis = {
                "count": int(len(series)),
                "missing_count": int(self.df[col].isnull().sum()),
                "unique_count": int(series.nunique()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "mode": float(series.mode().iloc[0])
                if not series.mode().empty
                else None,
                "std": float(series.std()),
                "variance": float(series.var()),
                "min": float(series.min()),
                "max": float(series.max()),
                "range": float(series.max() - series.min()),
                "q1": float(series.quantile(0.25)),
                "q3": float(series.quantile(0.75)),
                "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
                "skewness": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
            }

            # Outlier detection using IQR method
            q1, q3 = analysis["q1"], analysis["q3"]
            iqr = analysis["iqr"]
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = series[(series < lower_bound) | (series > upper_bound)]

            analysis["outliers"] = {
                "count": int(len(outliers)),
                "percentage": round(len(outliers) / len(series) * 100, 2),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            }

            # Distribution analysis
            try:
                # Test for normality
                _, p_value = stats.normaltest(series)
                analysis["normality_test"] = {
                    "is_normal": p_value > 0.05,
                    "p_value": float(p_value),
                }
            except Exception as e:
                analysis["normality_test"] = {
                    "error": f"Could not perform normality test: {str(e)}"
                }

            numeric_analysis[col] = analysis

        self.analysis_results["numeric_analysis"] = numeric_analysis
        return numeric_analysis

    def analyze_categorical_columns(self) -> dict[str, dict[str, Any]]:
        """Analyze categorical columns with frequency analysis."""
        print("\n📝 Analyzing categorical columns...")

        categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns
        categorical_analysis = {}

        for col in categorical_cols:
            print(f"  📊 Analyzing {col}")
            series = self.df[col].dropna()

            if len(series) == 0:
                categorical_analysis[col] = {"error": "No non-null values"}
                continue

            value_counts = series.value_counts()

            analysis = {
                "count": int(len(series)),
                "missing_count": int(self.df[col].isnull().sum()),
                "unique_count": int(series.nunique()),
                "most_frequent": str(value_counts.index[0])
                if not value_counts.empty
                else None,
                "most_frequent_count": int(value_counts.iloc[0])
                if not value_counts.empty
                else 0,
                "least_frequent": str(value_counts.index[-1])
                if not value_counts.empty
                else None,
                "least_frequent_count": int(value_counts.iloc[-1])
                if not value_counts.empty
                else 0,
            }

            # Top 10 most frequent values
            top_values = value_counts.head(10)
            analysis["top_10_values"] = {
                "values": top_values.index.tolist(),
                "counts": top_values.values.tolist(),
                "percentages": (top_values / len(series) * 100).round(2).tolist(),
            }

            # Calculate entropy (measure of diversity)
            probabilities = value_counts / len(series)
            entropy = -np.sum(probabilities * np.log2(probabilities))
            analysis["entropy"] = float(entropy)

            categorical_analysis[col] = analysis

        self.analysis_results["categorical_analysis"] = categorical_analysis
        return categorical_analysis

    def generate_distribution_plots(self) -> None:
        """Generate distribution plots for all columns."""
        print("\n📈 Generating distribution plots...")

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns

        # Numeric distributions
        if len(numeric_cols) > 0:
            n_cols = min(3, len(numeric_cols))
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()

            for i, col in enumerate(numeric_cols):
                ax = axes[i] if len(numeric_cols) > 1 else axes[0]

                # Create histogram with KDE
                data = self.df[col].dropna()
                if len(data) > 0:
                    ax.hist(
                        data,
                        bins=30,
                        alpha=0.7,
                        density=True,
                        color="skyblue",
                        edgecolor="black",
                    )

                    # Add KDE if enough data points
                    if len(data) > 10:
                        data_range = np.linspace(data.min(), data.max(), 100)
                        kde = stats.gaussian_kde(data)
                        ax.plot(
                            data_range, kde(data_range), "r-", linewidth=2, label="KDE"
                        )
                        ax.legend()

                    ax.set_title(f"Distribution of {col}")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Density")
                    ax.grid(True, alpha=0.3)

            # Hide empty subplots
            for i in range(len(numeric_cols), len(axes)):
                axes[i].set_visible(False)

            plt.tight_layout()
            plt.savefig(
                self.output_dir / "plots" / "numeric_distributions.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

        # Categorical distributions (top categories only)
        if len(categorical_cols) > 0:
            for col in categorical_cols[:6]:  # Limit to first 6 categorical columns
                plt.figure(figsize=(12, 6))

                value_counts = self.df[col].value_counts().head(15)  # Top 15 categories

                if len(value_counts) > 0:
                    ax = value_counts.plot(kind="bar", color="lightcoral")
                    plt.title(f"Top Categories in {col}")
                    plt.xlabel(col)
                    plt.ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    plt.grid(True, alpha=0.3)

                    # Add value labels on bars
                    for i, v in enumerate(value_counts):
                        ax.text(
                            i,
                            v + max(value_counts) * 0.01,
                            str(v),
                            ha="center",
                            va="bottom",
                        )

                plt.tight_layout()
                plt.savefig(
                    self.output_dir
                    / "plots"
                    / f"categorical_{col.replace(' ', '_')}.png",
                    dpi=300,
                    bbox_inches="tight",
                )
                plt.close()

    def generate_correlation_analysis(self) -> dict[str, Any]:
        """Generate correlation analysis for numeric columns."""
        print("\n🔗 Analyzing correlations...")

        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) < 2:
            print("  ⚠️ Need at least 2 numeric columns for correlation analysis")
            return {"error": "Insufficient numeric columns"}

        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()

        # Generate correlation heatmap
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            cmap="coolwarm",
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            fmt=".2f",
        )
        plt.title("Correlation Matrix of Numeric Variables")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "plots" / "correlation_matrix.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Strong correlation threshold
                    strong_correlations.append(
                        {
                            "variable1": corr_matrix.columns[i],
                            "variable2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                            "strength": "Strong"
                            if abs(corr_value) > 0.7
                            else "Moderate",
                        }
                    )

        correlation_analysis = {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "highest_correlation": max(
                strong_correlations, key=lambda x: abs(x["correlation"]), default=None
            ),
        }

        self.analysis_results["correlation_analysis"] = correlation_analysis
        return correlation_analysis

    def generate_data_quality_report(self) -> dict[str, Any]:
        """Generate data quality assessment."""
        print("\n🔍 Assessing data quality...")

        quality_report = {
            "completeness": {},
            "consistency": {},
            "validity": {},
            "overall_score": 0,
        }

        # Completeness analysis
        missing_percentage = self.df.isnull().sum() / len(self.df) * 100
        quality_report["completeness"] = {
            "overall_completeness": round(100 - missing_percentage.mean(), 2),
            "columns_completeness": (100 - missing_percentage).to_dict(),
            "columns_with_issues": missing_percentage[
                missing_percentage > 10
            ].to_dict(),
        }

        # Consistency analysis
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        consistency_issues = []

        for col in numeric_cols:
            if col in self.analysis_results.get("numeric_analysis", {}):
                outlier_percentage = (
                    self.analysis_results["numeric_analysis"][col]
                    .get("outliers", {})
                    .get("percentage", 0)
                )
                if outlier_percentage > 5:  # More than 5% outliers
                    consistency_issues.append(
                        {
                            "column": col,
                            "issue": "High outlier percentage",
                            "value": outlier_percentage,
                        }
                    )

        quality_report["consistency"] = {
            "issues_found": len(consistency_issues),
            "issues": consistency_issues,
        }

        # Calculate overall quality score
        completeness_score = quality_report["completeness"]["overall_completeness"]
        consistency_score = max(0, 100 - len(consistency_issues) * 10)

        quality_report["overall_score"] = round(
            (completeness_score + consistency_score) / 2, 2
        )

        self.analysis_results["data_quality"] = quality_report
        return quality_report

    def save_results(self, format_type: str = "json") -> None:
        """Save analysis results to files."""
        print(f"\n💾 Saving results in {format_type} format...")

        if format_type.lower() == "json":
            # Save JSON report
            with open(self.output_dir / "reports" / "analysis_report.json", "w") as f:
                json.dump(self.analysis_results, f, indent=2, default=str)

        elif format_type.lower() == "html":
            # Generate HTML report
            self._generate_html_report()

        # Always save a summary text report
        self._generate_text_summary()

        print(f"✅ Results saved to {self.output_dir}")

    def _generate_html_report(self) -> None:
        """Generate an HTML report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Analysis Report - {self.csv_path.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007bff; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .plot {{ text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Analysis Report</h1>
                <p><strong>File:</strong> {self.csv_path.name}</p>
                <p><strong>Generated:</strong> {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        """

        # Basic info section
        basic_info = self.analysis_results.get("basic_info", {})
        html_content += f"""
            <div class="section">
                <h2>📊 Dataset Overview</h2>
                <div class="metric">Rows: {basic_info.get("total_rows", "N/A")}</div>
                <div class="metric">Columns: {basic_info.get("total_columns", "N/A")}</div>
                <div class="metric">Memory: {basic_info.get("memory_usage_mb", "N/A")} MB</div>
                <div class="metric">Missing Values: {basic_info.get("missing_values", {}).get("total_missing", "N/A")}</div>
            </div>
        """

        # Data quality section
        quality = self.analysis_results.get("data_quality", {})
        html_content += f"""
            <div class="section">
                <h2>🔍 Data Quality Score</h2>
                <div class="metric" style="font-size: 24px; background-color: {"#d4edda" if quality.get("overall_score", 0) > 80 else "#fff3cd" if quality.get("overall_score", 0) > 60 else "#f8d7da"};">
                    {quality.get("overall_score", "N/A")}%
                </div>
            </div>
        """

        # Add plots
        plot_files = list((self.output_dir / "plots").glob("*.png"))
        if plot_files:
            html_content += '<div class="section"><h2>📈 Visualizations</h2>'
            for plot_file in plot_files:
                html_content += f'<div class="plot"><img src="plots/{plot_file.name}" alt="{plot_file.stem}" style="max-width: 100%; height: auto;"></div>'
            html_content += "</div>"

        html_content += """
        </body>
        </html>
        """

        with open(self.output_dir / "reports" / "analysis_report.html", "w") as f:
            f.write(html_content)

    def _generate_text_summary(self) -> None:
        """Generate a text summary report."""
        summary = f"""
DATA ANALYSIS SUMMARY
====================
File: {self.csv_path.name}
Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}

DATASET OVERVIEW
---------------
"""

        basic_info = self.analysis_results.get("basic_info", {})
        summary += f"• Total Rows: {basic_info.get('total_rows', 'N/A')}\n"
        summary += f"• Total Columns: {basic_info.get('total_columns', 'N/A')}\n"
        summary += f"• Memory Usage: {basic_info.get('memory_usage_mb', 'N/A')} MB\n"
        summary += f"• Missing Values: {basic_info.get('missing_values', {}).get('total_missing', 'N/A')}\n\n"

        # Numeric columns summary
        numeric_analysis = self.analysis_results.get("numeric_analysis", {})
        if numeric_analysis:
            summary += "NUMERIC COLUMNS\n"
            summary += "---------------\n"
            for col, stats in numeric_analysis.items():
                if "error" not in stats:
                    summary += f"• {col}:\n"
                    summary += f"  - Mean: {stats.get('mean', 'N/A'):.2f}\n"
                    summary += f"  - Std Dev: {stats.get('std', 'N/A'):.2f}\n"
                    summary += f"  - Missing: {stats.get('missing_count', 'N/A')}\n"
                    summary += f"  - Outliers: {stats.get('outliers', {}).get('count', 'N/A')}\n\n"

        # Categorical columns summary
        categorical_analysis = self.analysis_results.get("categorical_analysis", {})
        if categorical_analysis:
            summary += "CATEGORICAL COLUMNS\n"
            summary += "-------------------\n"
            for col, stats in categorical_analysis.items():
                if "error" not in stats:
                    summary += f"• {col}:\n"
                    summary += (
                        f"  - Unique Values: {stats.get('unique_count', 'N/A')}\n"
                    )
                    summary += (
                        f"  - Most Frequent: {stats.get('most_frequent', 'N/A')}\n"
                    )
                    summary += f"  - Missing: {stats.get('missing_count', 'N/A')}\n\n"

        # Data quality
        quality = self.analysis_results.get("data_quality", {})
        summary += "DATA QUALITY\n"
        summary += "------------\n"
        summary += f"• Overall Score: {quality.get('overall_score', 'N/A')}%\n"
        summary += f"• Completeness: {quality.get('completeness', {}).get('overall_completeness', 'N/A')}%\n"
        summary += f"• Issues Found: {quality.get('consistency', {}).get('issues_found', 'N/A')}\n\n"

        with open(self.output_dir / "reports" / "summary.txt", "w") as f:
            f.write(summary)

    def run_full_analysis(self, format_type: str = "json") -> None:
        """Run complete analysis pipeline."""
        print("🚀 Starting comprehensive data analysis...")

        # Load data
        self.load_data()

        # Run all analyses
        self.basic_info()
        self.analyze_numeric_columns()
        self.analyze_categorical_columns()
        self.generate_distribution_plots()
        self.generate_correlation_analysis()
        self.generate_data_quality_report()

        # Save results
        self.save_results(format_type)

        print(f"\n🎉 Analysis complete! Check results in: {self.output_dir}")
        print(
            f"📊 Summary: {self.analysis_results['basic_info']['total_rows']} rows, "
            f"{self.analysis_results['basic_info']['total_columns']} columns"
        )
        print(
            f"🔍 Data Quality Score: {self.analysis_results['data_quality']['overall_score']}%"
        )


def main():
    """Main function to run the data analyzer."""
    parser = argparse.ArgumentParser(
        description="Comprehensive CSV Data Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/data_analyzer.py data.csv
  python tools/data_analyzer.py data.csv --output-dir my_analysis
  python tools/data_analyzer.py data.csv --format html
  python tools/data_analyzer.py data.csv --output-dir results --format html
        """,
    )

    parser.add_argument("csv_file", help="Path to the CSV file to analyze")

    parser.add_argument(
        "--output-dir",
        default="analysis_output",
        help="Directory to save analysis results (default: analysis_output)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "html"],
        default="json",
        help="Output format for the report (default: json)",
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.csv_file).exists():
        print(f"❌ Error: File '{args.csv_file}' not found")
        sys.exit(1)

    # Run analysis
    try:
        analyzer = DataAnalyzer(args.csv_file, args.output_dir)
        analyzer.run_full_analysis(args.format)
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
