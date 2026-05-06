from typing import TypedDict, List, Literal
from datetime import date, datetime, timezone, timedelta


class Invoice(TypedDict):
    dueDate: date
    status: Literal["PAID", "UNPAID"]


class CreditReport(TypedDict):
    paymentHistory: List[Invoice]
    creditUtilisationPercentage: float


class CreditScore(TypedDict):
    value: int
    category: Literal["fair", "good", "excellent", "poor", "very poor"]


def get_credit_score(credit_report: dict, current_utc_time: datetime = None) -> dict:
    if current_utc_time is None:
        current_utc_time = datetime.now(timezone.utc)

    # 1. Base Utilisation Math (From Original Codebase)
    utilisation = credit_report.get('creditUtilisationPercentage', 0.0)
    
    if utilisation < 0.3:
        score_value = 999
    elif utilisation < 0.5:
        score_value = 960
    elif utilisation < 0.7:
        score_value = 880
    elif utilisation < 0.9:
        score_value = 720
    else:
        score_value = 560
        
    # 2. Payment History Penalties (New Requirement)
    payment_history = credit_report.get('paymentHistory', [])
    if payment_history:
        # Calculate the date exactly 2 years (approx 730 days) ago
        two_years_ago = current_utc_time - timedelta(days=730)

        applicable_invoices = [
            inv for inv in payment_history 
            if inv['dueDate'] >= two_years_ago 
            and (inv['status'] == 'PAID' or inv['dueDate'] < current_utc_time)
        ]
        
        if applicable_invoices:
            total_applicable = len(applicable_invoices)
            paid_count = sum(1 for inv in applicable_invoices if inv['status'] == 'PAID')
            
            # Simple percentage helper
            paid_percentage = round((paid_count / total_applicable), 2) if total_applicable else 1.0
            
            unpaid_percentage = round(1.0 - paid_percentage, 2)
            score_value -= int(unpaid_percentage * 100 * 5)
            
    score_value = max(0, score_value)
    
    # 3. Category Math (From Original Codebase)
    if score_value >= 961:
        category = "excellent"
    elif score_value >= 881:
        category = "good"
    elif score_value >= 721:
        category = "fair"
    elif score_value >= 561:
        category = "poor"
    else:
        category = "very poor"
        
    return {
        'value': score_value,
        'category': category
    }


def calculate_percentage(value: float, total: float) -> float:
    return round((value / total) * 100) / 100
