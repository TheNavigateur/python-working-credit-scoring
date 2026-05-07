from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum

class InvoiceStatus(str, Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"

class CreditScoreCategory(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very poor"

class Invoice(BaseModel):
    dueDate: datetime
    status: InvoiceStatus


class CreditReport(BaseModel):
    paymentHistory: List[Invoice]
    creditUtilisationPercentage: float


class CreditScore(BaseModel):
    value: int
    category: CreditScoreCategory


SCORE_THRESHOLDS_DESCENDING = sorted([
    (961, CreditScoreCategory.EXCELLENT),
    (881, CreditScoreCategory.GOOD),
    (721, CreditScoreCategory.FAIR),
    (561, CreditScoreCategory.POOR)
], reverse=True)


CREDIT_UTILIZATION_THRESHOLDS_DESCENDING = sorted([
    (0.9, 560),
    (0.7, 720),
    (0.5, 880),
    (0.3, 960)
], reverse=True)


# def evaluate_thresholds[T](value: float, thresholds: List[Tuple[float, T]], default: T, inclusive: bool = True) -> T:
#    for threshold, result in 

def get_credit_score(c: CreditReport, current_datetime: datetime = None) -> CreditScore:

    if current_datetime is None:
        current_datetime = datetime.now(tz=timezone.utc)

    x = c.creditUtilisationPercentage

    score_value = 999
    category: CreditScoreCategory = CreditScoreCategory.EXCELLENT

    if 0.3 < x <= 0.5:
        score_value = 960
    elif 0.5 < x <= 0.7:
        score_value = 880
    elif 0.7 < x <= 0.9:
        score_value = 720
    elif x > 0.9:
        score_value = 560

    if c.paymentHistory:
        two_years_ago = current_datetime - timedelta(days=2*365)
        applicable_invoices = [
            invoice for invoice in c.paymentHistory
            if invoice.dueDate > two_years_ago
            and (invoice.status == InvoiceStatus.PAID or invoice.dueDate < current_datetime)
        ]

        if applicable_invoices:
            total_applicable = len(applicable_invoices)
            unpaid_count = sum(1 for invoice in applicable_invoices if invoice.status == InvoiceStatus.UNPAID)
            unpaid_fraction = unpaid_count / total_applicable
            unpaid_percent_rounded_down = int(unpaid_fraction * 100)
            penalty = unpaid_percent_rounded_down * 5
            score_value -= penalty
            
    if score_value >= 961:
        category = CreditScoreCategory.EXCELLENT
    elif score_value >= 881:
        category = CreditScoreCategory.GOOD
    elif score_value >= 721:
        category = CreditScoreCategory.FAIR
    elif score_value >= 561:
        category = CreditScoreCategory.POOR
    else:
        category = CreditScoreCategory.VERY_POOR

    return CreditScore(value=score_value, category=category)


def calculate_percentage(value: float, total: float) -> float:
    return round((value / total) * 100) / 100
