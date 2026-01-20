import json
import pandas as pd
from collections import defaultdict

def load_extracted_bids(json_path="./extracted_bids.json"):
    """Load extracted bid data from JSON"""
    with open(json_path, "r") as f:
        return json.load(f)


def build_comparison_table(all_bids):
    """
    Build a comparison table: Plan vs Files
    
    Returns DataFrame like:
    | Plan  | File1.pdf | File2.xlsx | File3.pdf | Winner |
    |-------|-----------|------------|-----------|--------|
    | 4101  | $9,425    | $8,339     | $8,500    | File2  |
    """
    
    # Collect all unique plans across all files
    all_plans = set()
    for file_name, plans in all_bids.items():
        for plan in plans:
            plan_num = plan.get("plan_number")
            if plan_num:
                all_plans.add(plan_num)
    
    all_plans = sorted(all_plans)
    
    # Build comparison data
    comparison_data = []
    
    for plan_num in all_plans:
        row = {"Plan": plan_num}
        prices = {}
        
        for file_name, plans in all_bids.items():
            # Find this plan in this file
            plan_data = next(
                (p for p in plans if p.get("plan_number") == plan_num), 
                None
            )
            
            if plan_data and plan_data.get("total_price"):
                price = plan_data["total_price"]
                row[file_name] = price
                prices[file_name] = price
            else:
                row[file_name] = None
        
        # Determine winner (lowest price)
        if prices:
            winner = min(prices, key=prices.get)
            row["Winner"] = winner
            row["Best_Price"] = prices[winner]
        else:
            row["Winner"] = "N/A"
            row["Best_Price"] = None
        
        comparison_data.append(row)
    
    return pd.DataFrame(comparison_data)


def calculate_file_scores(comparison_df, all_bids):
    """
    Calculate which file wins overall based on:
    1. Number of plans won
    2. Total savings
    """
    
    file_names = list(all_bids.keys())
    
    scores = {file: {
        "plans_won": 0,
        "plans_won_list": [],
        "total_if_chosen": 0,
        "plans_available": 0
    } for file in file_names}
    
    for _, row in comparison_df.iterrows():
        plan = row["Plan"]
        winner = row["Winner"]
        
        if winner != "N/A" and winner in scores:
            scores[winner]["plans_won"] += 1
            scores[winner]["plans_won_list"].append(plan)
        
        # Calculate totals for each file
        for file in file_names:
            if pd.notna(row.get(file)):
                scores[file]["total_if_chosen"] += row[file]
                scores[file]["plans_available"] += 1
    
    return scores


def generate_report(all_bids, output_path="./bid_comparison_report.txt"):
    """Generate comprehensive comparison report"""
    comparison_df = build_comparison_table(all_bids)
    scores = calculate_file_scores(comparison_df, all_bids)
    
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("BID COMPARISON REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Files analyzed
    report_lines.append(" FILES ANALYZED:")
    report_lines.append("-" * 40)
    for i, file_name in enumerate(all_bids.keys(), 1):
        plan_count = len(all_bids[file_name])
        report_lines.append(f" {i}. {file_name} ({plan_count} plans)")
    report_lines.append("")
    
    # Plan-by-Plan Comparison
    report_lines.append(" PLAN-BY-PLAN COMPARISON:")
    report_lines.append("-" * 40)
    report_lines.append("")
    
    for _, row in comparison_df.iterrows():
        plan = row["Plan"]
        winner = row["Winner"]
        report_lines.append(f"Plan {plan}:")
        
        # Show price from each file
        for file_name in all_bids.keys():
            price = row.get(file_name)
            if pd.notna(price):
                marker = " ✓ LOWEST" if file_name == winner else ""
                report_lines.append(f" • {file_name}: ${price:,.2f}{marker}")
            else:
                report_lines.append(f" • {file_name}: N/A")
        report_lines.append("")
    
    # File Scores Summary
    report_lines.append("=" * 80)
    report_lines.append(" FILE SCORES SUMMARY:")
    report_lines.append("-" * 40)
    
    # Sort by plans won
    sorted_scores = sorted(scores.items(), 
                          key=lambda x: x[1]["plans_won"], 
                          reverse=True)
    
    for rank, (file_name, score) in enumerate(sorted_scores, 1):
        report_lines.append(f"\n#{rank} {file_name}")
        report_lines.append(f" Plans Won: {score['plans_won']} out of {len(comparison_df)}")
        report_lines.append(f" Win Rate: {score['plans_won']/len(comparison_df)*100:.1f}%")
        report_lines.append(f" Total (if chosen): ${score['total_if_chosen']:,.2f}")
        if score['plans_won_list']:
            report_lines.append(f" Won Plans: {', '.join(score['plans_won_list'])}")
    
    # Overall Winner
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append(" OVERALL WINNER:")
    report_lines.append("=" * 80)
    
    winner_file = sorted_scores[0][0]
    winner_score = sorted_scores[0][1]
    
    report_lines.append(f"\n {winner_file}")
    report_lines.append(f"\n Reason:")
    report_lines.append(f" • Won {winner_score['plans_won']} out of {len(comparison_df)} plans")
    report_lines.append(f" • Win rate: {winner_score['plans_won']/len(comparison_df)*100:.1f}%")
    
    # Calculate savings vs others
    if len(sorted_scores) > 1:
        report_lines.append(f"\n Savings compared to other bids:")
        for file_name, score in sorted_scores[1:]:
            if score['total_if_chosen'] > 0:
                savings = score['total_if_chosen'] - winner_score['total_if_chosen']
                report_lines.append(f" • vs {file_name}: ${savings:,.2f} savings")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    
    # Write report with UTF-8 encoding
    report_text = "\n".join(report_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n Report saved to {output_path}")
    
    # Also save comparison table as CSV
    csv_path = "./bid_comparison_table.csv"
    comparison_df.to_csv(csv_path, index=False)
    print(f" Comparison table saved to {csv_path}")
    
    return comparison_df, scores


if __name__ == "__main__":
    print("Loading extracted bid data...")
    all_bids = load_extracted_bids()
    
    print("Generating comparison report...")
    comparison_df, scores = generate_report(all_bids)
