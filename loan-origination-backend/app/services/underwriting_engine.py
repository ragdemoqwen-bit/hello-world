"""
Automated Underwriting Engine

Evaluates loan applications based on credit score, DTI ratio,
LTV ratio (for secured loans), and other risk factors to produce
an underwriting decision.
"""

import json
from dataclasses import dataclass

from app.models.underwriting import UnderwritingDecision, RiskLevel


@dataclass
class UnderwritingInput:
    credit_score: int
    annual_income: float
    monthly_debt_payments: float
    requested_amount: float
    loan_term_months: int
    loan_type: str
    property_value: float | None = None
    bankruptcies: int = 0
    collections: int = 0
    delinquent_accounts: int = 0
    employment_verified: bool = True
    kyc_verified: bool = True


@dataclass
class UnderwritingOutput:
    credit_score: int
    dti_ratio: float
    ltv_ratio: float | None
    risk_score: float
    risk_level: RiskLevel
    decision: UnderwritingDecision
    conditions: list[str]
    denial_reasons: list[str]
    notes: str


# Thresholds
MIN_CREDIT_SCORE = 580
PREFERRED_CREDIT_SCORE = 700
MAX_DTI_RATIO = 0.50
PREFERRED_DTI_RATIO = 0.36
MAX_LTV_RATIO = 0.97
PREFERRED_LTV_RATIO = 0.80


def calculate_dti(
    annual_income: float,
    monthly_debt_payments: float,
    requested_amount: float,
    loan_term_months: int,
    interest_rate: float = 0.065,
) -> float:
    """Calculate Debt-to-Income ratio including the new loan payment."""
    monthly_income = annual_income / 12.0
    if monthly_income <= 0:
        return 999.0

    # Estimate monthly payment for new loan (simple amortization)
    monthly_rate = interest_rate / 12.0
    if monthly_rate > 0 and loan_term_months > 0:
        payment = (
            requested_amount
            * (monthly_rate * (1 + monthly_rate) ** loan_term_months)
            / ((1 + monthly_rate) ** loan_term_months - 1)
        )
    else:
        payment = requested_amount / max(loan_term_months, 1)

    total_monthly_debt = monthly_debt_payments + payment
    return round(total_monthly_debt / monthly_income, 4)


def calculate_ltv(requested_amount: float, property_value: float | None) -> float | None:
    """Calculate Loan-to-Value ratio for secured loans."""
    if property_value is None or property_value <= 0:
        return None
    return round(requested_amount / property_value, 4)


def calculate_risk_score(inputs: UnderwritingInput, dti: float, ltv: float | None) -> float:
    """
    Calculate a composite risk score (0-100, lower is better).

    Weights:
    - Credit score: 35%
    - DTI ratio: 30%
    - LTV ratio: 15% (secured loans only)
    - Derogatory marks: 10%
    - Employment/KYC: 10%
    """
    score = 0.0

    # Credit score component (0-35 points of risk)
    if inputs.credit_score >= 800:
        score += 0
    elif inputs.credit_score >= 740:
        score += 5
    elif inputs.credit_score >= 700:
        score += 12
    elif inputs.credit_score >= 660:
        score += 20
    elif inputs.credit_score >= 620:
        score += 28
    else:
        score += 35

    # DTI component (0-30 points of risk)
    if dti <= 0.28:
        score += 0
    elif dti <= 0.36:
        score += 8
    elif dti <= 0.43:
        score += 18
    elif dti <= 0.50:
        score += 25
    else:
        score += 30

    # LTV component (0-15 points of risk, for secured loans)
    if ltv is not None:
        if ltv <= 0.60:
            score += 0
        elif ltv <= 0.80:
            score += 5
        elif ltv <= 0.90:
            score += 10
        elif ltv <= 0.97:
            score += 13
        else:
            score += 15
    else:
        # Unsecured loan - add moderate risk
        score += 8

    # Derogatory marks (0-10 points of risk)
    score += min(inputs.bankruptcies * 5, 10)
    score += min(inputs.collections * 3, 6)
    score += min(inputs.delinquent_accounts * 2, 6)
    derog_score = min(inputs.bankruptcies * 5 + inputs.collections * 3 + inputs.delinquent_accounts * 2, 10)
    score = score - (min(inputs.bankruptcies * 5, 10) + min(inputs.collections * 3, 6) + min(inputs.delinquent_accounts * 2, 6)) + derog_score

    # Employment/KYC (0-10 points of risk)
    if not inputs.employment_verified:
        score += 7
    if not inputs.kyc_verified:
        score += 3

    return round(min(score, 100), 2)


def determine_risk_level(risk_score: float) -> RiskLevel:
    """Map risk score to risk level."""
    if risk_score <= 20:
        return RiskLevel.LOW
    elif risk_score <= 40:
        return RiskLevel.MEDIUM
    elif risk_score <= 60:
        return RiskLevel.HIGH
    else:
        return RiskLevel.VERY_HIGH


def run_underwriting(inputs: UnderwritingInput) -> UnderwritingOutput:
    """
    Run the full underwriting evaluation.

    Returns an UnderwritingOutput with the decision, conditions, and reasons.
    """
    dti = calculate_dti(
        inputs.annual_income,
        inputs.monthly_debt_payments,
        inputs.requested_amount,
        inputs.loan_term_months,
    )
    ltv = calculate_ltv(inputs.requested_amount, inputs.property_value)
    risk_score = calculate_risk_score(inputs, dti, ltv)
    risk_level = determine_risk_level(risk_score)

    conditions: list[str] = []
    denial_reasons: list[str] = []
    notes_parts: list[str] = []

    # --- Decision logic ---

    # Hard denials
    if inputs.credit_score < MIN_CREDIT_SCORE:
        denial_reasons.append(f"Credit score {inputs.credit_score} below minimum {MIN_CREDIT_SCORE}")

    if dti > MAX_DTI_RATIO:
        denial_reasons.append(f"DTI ratio {dti:.1%} exceeds maximum {MAX_DTI_RATIO:.0%}")

    if ltv is not None and ltv > MAX_LTV_RATIO:
        denial_reasons.append(f"LTV ratio {ltv:.1%} exceeds maximum {MAX_LTV_RATIO:.0%}")

    if not inputs.kyc_verified:
        denial_reasons.append("Identity verification failed")

    if inputs.bankruptcies >= 2:
        denial_reasons.append(f"Multiple bankruptcies ({inputs.bankruptcies}) on record")

    # If any hard denials, deny
    if denial_reasons:
        return UnderwritingOutput(
            credit_score=inputs.credit_score,
            dti_ratio=dti,
            ltv_ratio=ltv,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=UnderwritingDecision.DENIED,
            conditions=[],
            denial_reasons=denial_reasons,
            notes="Application denied based on automated underwriting criteria.",
        )

    # Conditional approvals
    if inputs.credit_score < PREFERRED_CREDIT_SCORE:
        conditions.append("Additional income documentation required")

    if dti > PREFERRED_DTI_RATIO:
        conditions.append("Compensating factors required for elevated DTI")

    if ltv is not None and ltv > PREFERRED_LTV_RATIO:
        conditions.append("Private mortgage insurance (PMI) required")

    if not inputs.employment_verified:
        conditions.append("Employment verification must be completed")

    if inputs.collections > 0:
        conditions.append("Explanation letter required for collections accounts")

    if inputs.delinquent_accounts > 0:
        conditions.append("Explanation letter required for delinquent accounts")

    # Manual review for high risk
    if risk_level == RiskLevel.HIGH:
        notes_parts.append("Elevated risk - recommend senior underwriter review")
        return UnderwritingOutput(
            credit_score=inputs.credit_score,
            dti_ratio=dti,
            ltv_ratio=ltv,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=UnderwritingDecision.MANUAL_REVIEW,
            conditions=conditions,
            denial_reasons=[],
            notes="; ".join(notes_parts) if notes_parts else "Requires manual review due to risk factors.",
        )

    # Conditional vs full approval
    if conditions:
        decision = UnderwritingDecision.CONDITIONALLY_APPROVED
        notes_parts.append("Conditionally approved pending satisfaction of listed conditions")
    else:
        decision = UnderwritingDecision.APPROVED
        notes_parts.append("Application meets all automated underwriting criteria")

    return UnderwritingOutput(
        credit_score=inputs.credit_score,
        dti_ratio=dti,
        ltv_ratio=ltv,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        conditions=conditions,
        denial_reasons=[],
        notes="; ".join(notes_parts),
    )


def calculate_interest_rate(credit_score: int, loan_type: str, ltv: float | None) -> float:
    """
    Determine the interest rate based on credit profile and loan characteristics.
    Returns annual interest rate as a decimal (e.g., 0.065 for 6.5%).
    """
    # Base rates by loan type
    base_rates = {
        "mortgage": 0.065,
        "auto": 0.072,
        "personal": 0.095,
        "business": 0.085,
        "student": 0.055,
    }
    base = base_rates.get(loan_type, 0.085)

    # Credit score adjustment
    if credit_score >= 800:
        base -= 0.010
    elif credit_score >= 740:
        base -= 0.005
    elif credit_score >= 700:
        pass  # no adjustment
    elif credit_score >= 660:
        base += 0.010
    elif credit_score >= 620:
        base += 0.020
    else:
        base += 0.035

    # LTV adjustment (mortgage)
    if ltv is not None:
        if ltv > 0.90:
            base += 0.005
        elif ltv > 0.80:
            base += 0.0025

    return round(base, 4)


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """Calculate monthly payment using amortization formula."""
    monthly_rate = annual_rate / 12.0
    if monthly_rate <= 0 or term_months <= 0:
        return round(principal / max(term_months, 1), 2)
    payment = (
        principal
        * (monthly_rate * (1 + monthly_rate) ** term_months)
        / ((1 + monthly_rate) ** term_months - 1)
    )
    return round(payment, 2)
