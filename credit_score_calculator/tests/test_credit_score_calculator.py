import pytest
from credit_score_calculator.credit_score_calculator import CreditReport, CreditScoreCategory, get_credit_score
from datetime import datetime, timezone

@pytest.mark.parametrize("utilisation, expected_score, expected_category", [
    (0.95, 560, CreditScoreCategory.VERY_POOR),
    (0.9, 720, CreditScoreCategory.POOR), # 0.9 boundary check
    (0.8, 720, CreditScoreCategory.POOR),
    (0.7, 880, CreditScoreCategory.FAIR), # 0.7 boundary check
    (0.6, 880, CreditScoreCategory.FAIR),
    (0.5, 960, CreditScoreCategory.GOOD), # 0.5 boundary check
    (0.4, 960, CreditScoreCategory.GOOD),
    (0.3, 999, CreditScoreCategory.EXCELLENT), # 0.3 boundary check
    (0.2, 999, CreditScoreCategory.EXCELLENT),
])
def test_for_expected_score_and_category_for_credit_utilisation(utilisation, expected_score, expected_category: CreditScoreCategory):
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': utilisation,
    }

    credit_score = get_credit_score(CreditReport(**credit_report))

    assert credit_score.value == expected_score
    assert credit_score.category == expected_category


"""
    Deduct 5 points for every 1% of invoices that are unpaid
    Ignore future invoices and those older than 2 years
"""

def test_for_ignoring_future_invoices():
    credit_report = {
        'paymentHistory': [
            {'dueDate': datetime(2026, 5, 8, tzinfo=timezone.utc), 'status': 'UNPAID'},
        ],
        'creditUtilisationPercentage': 0.2,
    }

    credit_score = get_credit_score(CreditReport(**credit_report), current_datetime=datetime(2026, 5, 7, tzinfo=timezone.utc))

    assert credit_score.value == 999
    assert credit_score.category == CreditScoreCategory.EXCELLENT

def test_for_ignoring_old_invoices():
    credit_report = {
        'paymentHistory': [
            {'dueDate': datetime(2024, 5, 7, tzinfo=timezone.utc), 'status': 'UNPAID'},
        ],
        'creditUtilisationPercentage': 0.2,
    }

    credit_score = get_credit_score(CreditReport(**credit_report), current_datetime=datetime(2026, 5, 7, tzinfo=timezone.utc))

    assert credit_score.value == 999
    assert credit_score.category == CreditScoreCategory.EXCELLENT

def test_for_unpaid_invoices_penalty():
    credit_report = {
        'paymentHistory': [
            {'dueDate': datetime(2026, 1, 1, tzinfo=timezone.utc), 'status': 'UNPAID'},
            {'dueDate': datetime(2026, 1, 2, tzinfo=timezone.utc), 'status': 'PAID'},
            {'dueDate': datetime(2026, 1, 3, tzinfo=timezone.utc), 'status': 'PAID'},
            {'dueDate': datetime(2026, 1, 4, tzinfo=timezone.utc), 'status': 'PAID'},
        ],
        'creditUtilisationPercentage': 0.2,
    }

    credit_score = get_credit_score(CreditReport(**credit_report), current_datetime=datetime(2026, 5, 7, tzinfo=timezone.utc))

    """
        Expected score:

        999 - 
        (25 * 5)

        = 874
    """
    assert credit_score.value == 874
    assert credit_score.category == CreditScoreCategory.FAIR