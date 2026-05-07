from credit_score_calculator.credit_score_calculator import get_credit_score

def test_credit_score_calculator_returns_560_for_credit_utilisation_more_than_90_percent():
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': 0.95,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 560
    assert credit_score['category'] == 'very poor'

def test_credit_score_calculator_returns_720_for_credit_utilisation_between_70_and_90_percent():
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': 0.8,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 720
    assert credit_score['category'] == 'poor'

def test_credit_score_calculator_returns_880_for_credit_utilisation_between_50_and_70_percent():
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': 0.6,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 880
    assert credit_score['category'] == 'fair'

def test_credit_score_calculator_returns_960_for_credit_utilisation_between_30_and_50_percent():
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': 0.4,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 960
    assert credit_score['category'] == 'good'

def test_credit_score_calculator_returns_999_for_credit_utilisation_less_than_30_percent():
    credit_report = {
        'paymentHistory': [],
        'creditUtilisationPercentage': 0.2,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 999
    assert credit_score['category'] == 'excellent'

def test_credit_score_penalizes_for_unpaid_invoices():
    from datetime import datetime, timezone
    credit_report = {
        'paymentHistory': [
            {'dueDate': datetime(2023, 1, 1, tzinfo=timezone.utc), 'status': 'PAID'},
            {'dueDate': datetime(2023, 1, 1, tzinfo=timezone.utc), 'status': 'UNPAID'},
        ],
        'creditUtilisationPercentage': 0.2,
    }

    credit_score = get_credit_score(credit_report)

    assert credit_score['value'] == 999
    assert credit_score['category'] == 'excellent'