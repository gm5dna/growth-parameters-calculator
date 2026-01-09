"""
Calculation functions for growth parameters
"""
import math
from dateutil.relativedelta import relativedelta
from constants import (
    DAYS_PER_YEAR, MONTHS_PER_YEAR,
    FULL_TERM_WEEKS, FULL_TERM_DAYS, DAYS_PER_WEEK,
    PRETERM_THRESHOLD_WEEKS, MODERATE_PRETERM_THRESHOLD_WEEKS,
    CORRECTION_AGE_THRESHOLD_MODERATE, CORRECTION_AGE_THRESHOLD_EXTREME,
    GH_DOSE_STANDARD, WEIGHT_TO_GRAMS
)


def calculate_age_in_years(birth_date, measurement_date):
    """
    Calculate age in decimal years and calendar age

    Args:
        birth_date: Date of birth
        measurement_date: Date of measurement

    Returns:
        tuple: (decimal_years, calendar_age_dict)
    """
    delta = relativedelta(measurement_date, birth_date)
    years = delta.years
    months = delta.months
    days = delta.days

    # Convert to decimal years using constants
    decimal_years = years + (months / MONTHS_PER_YEAR) + (days / DAYS_PER_YEAR)

    # Calendar age
    calendar_age = {
        'years': years,
        'months': months,
        'days': days
    }

    return decimal_years, calendar_age


def should_apply_gestation_correction(gestation_weeks, gestation_days, chronological_age_years):
    """
    Determine if gestational age correction should be applied

    Args:
        gestation_weeks: Gestation at birth in weeks
        gestation_days: Additional days beyond gestation_weeks
        chronological_age_years: Current chronological age in decimal years

    Returns:
        bool: True if correction should be applied
    """
    if not gestation_weeks:
        return False

    total_gestation_weeks = gestation_weeks + (gestation_days or 0) / DAYS_PER_WEEK

    # Only apply correction for babies < 37 weeks gestation
    if total_gestation_weeks >= PRETERM_THRESHOLD_WEEKS:
        return False

    # 32-36 weeks: correction until age 1 year
    if MODERATE_PRETERM_THRESHOLD_WEEKS <= total_gestation_weeks < PRETERM_THRESHOLD_WEEKS:
        return chronological_age_years <= CORRECTION_AGE_THRESHOLD_MODERATE

    # < 32 weeks: correction until age 2 years
    if total_gestation_weeks < MODERATE_PRETERM_THRESHOLD_WEEKS:
        return chronological_age_years <= CORRECTION_AGE_THRESHOLD_EXTREME

    return False


def calculate_corrected_age(birth_date, measurement_date, gestation_weeks, gestation_days):
    """
    Calculate corrected age based on due date (EDD)

    Args:
        birth_date: Date of birth
        measurement_date: Date of measurement
        gestation_weeks: Gestation at birth in weeks
        gestation_days: Additional days beyond gestation_weeks

    Returns:
        tuple: (corrected_decimal_years, corrected_calendar_age_dict)
    """
    # Calculate expected due date
    total_gestation_days = (gestation_weeks * DAYS_PER_WEEK) + (gestation_days or 0)
    days_adjustment = FULL_TERM_DAYS - total_gestation_days

    # Corrected "birth" date is the estimated due date
    corrected_birth_date = birth_date + relativedelta(days=days_adjustment)

    # Calculate age from corrected birth date
    return calculate_age_in_years(corrected_birth_date, measurement_date)


def calculate_boyd_bsa(weight_kg, height_cm):
    """
    Calculate Body Surface Area using Boyd formula

    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters

    Returns:
        float: BSA in m² (rounded to 2 decimal places), or None if invalid
    """
    # Boyd formula: BSA = 0.0003207 * (height_cm^0.3) * (weight_g^(0.7285 - (0.0188 * log10(weight_g))))
    if weight_kg <= 0 or height_cm <= 0:
        return None

    weight_g = weight_kg * WEIGHT_TO_GRAMS
    log_weight = math.log10(weight_g)
    bsa = 0.0003207 * (height_cm ** 0.3) * (weight_g ** (0.7285 - (0.0188 * log_weight)))
    return round(bsa, 2)


def calculate_cbnf_bsa(weight_kg):
    """
    Calculate Body Surface Area from weight alone using cBNF lookup tables

    Based on tables from British National Formulary for Children (BNFc)
    Adapted from Sharkey I et al., British Journal of Cancer 2001; 85 (1): 23–28
    Values are calculated using the Boyd equation

    Args:
        weight_kg: Body weight in kilograms

    Returns:
        float: BSA in m² (rounded to 2 decimal places), or None if weight is invalid
    """
    if weight_kg <= 0:
        return None

    # cBNF lookup table: weight (kg) -> BSA (m²)
    lookup_table = {
        1: 0.10, 1.5: 0.13, 2: 0.16, 2.5: 0.19, 3: 0.21, 3.5: 0.24,
        4: 0.26, 4.5: 0.28, 5: 0.30, 5.5: 0.32, 6: 0.34, 6.5: 0.36,
        7: 0.38, 7.5: 0.40, 8: 0.42, 8.5: 0.44, 9: 0.46, 9.5: 0.47,
        10: 0.49, 11: 0.53, 12: 0.56, 13: 0.59, 14: 0.62, 15: 0.65,
        16: 0.68, 17: 0.71, 18: 0.74, 19: 0.77, 20: 0.79, 21: 0.82,
        22: 0.85, 23: 0.87, 24: 0.90, 25: 0.92, 26: 0.95, 27: 0.97,
        28: 1.0, 29: 1.0, 30: 1.1, 31: 1.1, 32: 1.1, 33: 1.1,
        34: 1.1, 35: 1.2, 36: 1.2, 37: 1.2, 38: 1.2, 39: 1.3, 40: 1.3,
        41: 1.3, 42: 1.3, 43: 1.3, 44: 1.4, 45: 1.4, 46: 1.4,
        47: 1.4, 48: 1.4, 49: 1.5, 50: 1.5, 51: 1.5, 52: 1.5,
        53: 1.5, 54: 1.6, 55: 1.6, 56: 1.6, 57: 1.6, 58: 1.6,
        59: 1.7, 60: 1.7, 61: 1.7, 62: 1.7, 63: 1.7, 64: 1.7,
        65: 1.8, 66: 1.8, 67: 1.8, 68: 1.8, 69: 1.8, 70: 1.9,
        71: 1.9, 72: 1.9, 73: 1.9, 74: 1.9, 75: 1.9, 76: 2.0,
        77: 2.0, 78: 2.0, 79: 2.0, 80: 2.0, 81: 2.0, 82: 2.1,
        83: 2.1, 84: 2.1, 85: 2.1, 86: 2.1, 87: 2.1, 88: 2.2,
        89: 2.2, 90: 2.2
    }

    # If exact weight is in the table, return it
    if weight_kg in lookup_table:
        return lookup_table[weight_kg]

    # For weights below 1 kg or above 90 kg, or between table values,
    # use linear interpolation between nearest values
    weights = sorted(lookup_table.keys())

    if weight_kg < weights[0]:
        # Extrapolate below minimum (use first two points)
        w1, w2 = weights[0], weights[1]
        bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
        slope = (bsa2 - bsa1) / (w2 - w1)
        bsa = bsa1 + slope * (weight_kg - w1)
    elif weight_kg > weights[-1]:
        # Extrapolate above maximum (use last two points)
        w1, w2 = weights[-2], weights[-1]
        bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
        slope = (bsa2 - bsa1) / (w2 - w1)
        bsa = bsa2 + slope * (weight_kg - w2)
    else:
        # Interpolate between two nearest values
        for i in range(len(weights) - 1):
            if weights[i] < weight_kg < weights[i + 1]:
                w1, w2 = weights[i], weights[i + 1]
                bsa1, bsa2 = lookup_table[w1], lookup_table[w2]
                # Linear interpolation
                slope = (bsa2 - bsa1) / (w2 - w1)
                bsa = bsa1 + slope * (weight_kg - w1)
                break

    return round(bsa, 2)


def calculate_height_velocity(current_height, previous_height, current_date, previous_date):
    """
    Calculate yearly derived height velocity

    Args:
        current_height: Current height in cm
        previous_height: Previous height in cm
        current_date: Current measurement date
        previous_date: Previous measurement date

    Returns:
        dict: With 'value' and optional 'message', or None
    """
    if not all([current_height, previous_height, current_date, previous_date]):
        return None

    height_diff = current_height - previous_height
    time_diff_days = (current_date - previous_date).days

    if time_diff_days <= 0:
        return {'value': None, 'message': 'Previous measurement date must be before current measurement date'}

    # Check if interval is at least 4 months (approximately 122 days)
    min_days = 122  # ~4 months
    if time_diff_days < min_days:
        months = round(time_diff_days / 30.44, 1)  # Convert to months for display
        return {
            'value': None,
            'message': f'Height velocity requires at least 4 months between measurements (current interval: {months} months)'
        }

    # Convert to cm per year
    velocity = (height_diff / time_diff_days) * DAYS_PER_YEAR
    return {'value': round(velocity, 1), 'message': None}


def calculate_gh_dose(bsa, weight_kg):
    """
    Calculate GH dose in mg/day for standard 7 mg/m²/week

    Args:
        bsa: Body surface area in m²
        weight_kg: Weight in kilograms

    Returns:
        dict: With mg_per_day, mg_m2_week, and mcg_kg_day, or None
    """
    if not bsa or not weight_kg:
        return None

    # Calculate for standard dose
    mg_per_week = GH_DOSE_STANDARD * bsa
    mg_per_day = mg_per_week / DAYS_PER_WEEK

    # Round to nearest 0.1 mg
    mg_per_day_rounded = round(mg_per_day, 1)

    # Calculate precise mg/m²/week from the rounded daily dose
    mg_per_week_actual = mg_per_day_rounded * DAYS_PER_WEEK
    mg_m2_week_actual = mg_per_week_actual / bsa

    # Calculate mcg/kg/day
    mcg_per_day = mg_per_day_rounded * WEIGHT_TO_GRAMS  # Convert mg to mcg
    mcg_kg_day = mcg_per_day / weight_kg

    return {
        'mg_per_day': mg_per_day_rounded,
        'mg_m2_week': round(mg_m2_week_actual, 1),
        'mcg_kg_day': round(mcg_kg_day, 1)
    }
