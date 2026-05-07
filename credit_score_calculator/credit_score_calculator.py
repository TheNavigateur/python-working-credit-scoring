from typing import TypedDict, List, Literal
from datetime import datetime, timezone


class Invoice(TypedDict):
    dueDate: datetime
    status: Literal["PAID", "UNPAID"]


class CreditReport(TypedDict):
    paymentHistory: List[Invoice]
    creditUtilisationPercentage: float


class CreditScore(TypedDict):
    value: int
    category: Literal["fair", "good", "excellent", "poor", "very poor"]


def get_credit_score(c: CreditReport, date_time_utc: datetime = None) -> CreditScore:

    if date_time_utc is None:
        date_time_utc = datetime.now(timezone.utc)

    credit_utilization_percentage = c['creditUtilisationPercentage']

    if 0.3 < credit_utilization_percentage <= 0.5:
        return {
            'value': 960,
            'category': 'good',
        }
    elif 0.5 < credit_utilization_percentage <= 0.7:
        return {
            'value': 880,
            'category': 'fair',
        }
    elif 0.7 < credit_utilization_percentage <= 0.9:
        return {
            'value': 720,
            'category': 'poor',
        }
    elif credit_utilization_percentage > 0.9:
        return {
            'value': 560,
            'category': 'very poor',
        }

    return {
        'value': 999,
        'category': 'excellent',
    }


def calculate_percentage(value: float, total: float) -> float:
    return round((value / total) * 100) / 100
