from typing import Tuple, List, Literal
from datetime import datetime, timezone, timedelta

from pydantic import BaseModel, computed_field


class Invoice(BaseModel):
    dueDate: datetime
    status: Literal["PAID", "UNPAID"]


class CreditReport(BaseModel):
    paymentHistory: List[Invoice]
    creditUtilisationPercentage: float

type CreditCategory = Literal["fair", "good", "excellent", "poor", "very poor"]

class CreditScore(BaseModel):
    value: int

    @computed_field
    @property
    def category(self) -> CreditCategory:
        return _get_category_for_score(self.value)

UTILISATION_THRESHOLDS_DESCENDING = sorted([
    (0.9, 560),
    (0.7, 720),
    (0.5, 880),
    (0.3, 960)
], reverse=True)

SCORE_THRESHOLDS_DESCENDING = sorted([
    (961, "excellent"),
    (881, "good"),
    (721, "fair"),
    (561, "poor")
], reverse=True)

def _evaluate_thresholds[T](value: float, thresholds: List[Tuple[float, T]], default: T, inclusive: bool = True) -> T:
    for threshold, result in thresholds:
        if (value >= threshold) if inclusive else (value > threshold):
            return result
    return default

def _get_category_for_score(score: int) -> str:
    return _evaluate_thresholds(score, SCORE_THRESHOLDS_DESCENDING, "very poor", inclusive=True)

def _get_base_score_for_utilisation(utilisation: float) -> int:
    return _evaluate_thresholds(utilisation, UTILISATION_THRESHOLDS_DESCENDING, 999, inclusive=False)

def get_credit_score(credit_report: CreditReport, current_utc_time: datetime = None) -> CreditScore:
    if current_utc_time is None:
        current_utc_time = datetime.now(timezone.utc)

    # 1. Base Utilisation Math (From Original Codebase)
    utilisation = credit_report.creditUtilisationPercentage

    score_value = _get_base_score_for_utilisation(utilisation)
        
    # 2. Payment History Penalties (New Requirement)
    payment_history = credit_report.paymentHistory
    if payment_history:
        # Calculate the date exactly 2 years (approx 730 days) ago
        two_years_ago = current_utc_time - timedelta(days=730)

        applicable_invoices = [
            inv for inv in payment_history 
            if inv.dueDate >= two_years_ago 
            and (inv.status == 'PAID' or inv.dueDate < current_utc_time)
        ]
        
        if applicable_invoices:
            total_applicable = len(applicable_invoices)
            paid_count = sum(1 for inv in applicable_invoices if inv.status == 'PAID')
            
            # Simple percentage helper
            paid_percentage = round((paid_count / total_applicable), 2) if total_applicable else 1.0
            
            unpaid_percentage = round(1.0 - paid_percentage, 2)
            score_value -= int(unpaid_percentage * 100 * 5)
            
    score_value = max(0, score_value)
        
    return CreditScore(value=score_value)

def calculate_percentage(value: float, total: float) -> float:
    return round((value / total) * 100) / 100
