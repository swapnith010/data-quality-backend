import pandas as pd

def calculate_quality(errors):
    if errors <= 10:
        return 98
    elif errors <= 30:
        return 90
    elif errors <= 50:
        return 78
    elif errors <= 100:
        return 65
    else:
        return 50


def analyze_file(filepath):
    df = pd.read_csv(filepath)

    rows, cols = df.shape

    error_list = []

    # Missing values
    missing_mask = df.isnull()

    # Invalid values
    invalid_mask = df.isin(["", "NA", "null"])

    # Duplicate rows
    duplicate_mask = df.duplicated()

    missing_count = missing_mask.sum().sum()
    invalid_count = invalid_mask.sum().sum()
    duplicate_count = duplicate_mask.sum()

    # Build error list
    for col in df.columns:
        for idx in df.index:
            if missing_mask.loc[idx, col]:
                error_list.append(f"Row {idx+1}, Column '{col}' → Missing value")

            elif invalid_mask.loc[idx, col]:
                error_list.append(f"Row {idx+1}, Column '{col}' → Invalid value")

    for idx in df.index:
        if duplicate_mask[idx]:
            error_list.append(f"Row {idx+1} → Duplicate row")

    total_errors = len(error_list)

    # ✅ NEW RANGE-BASED QUALITY SCORE
    quality_score = calculate_quality(total_errors)

    return {
        "rows": rows,
        "cols": cols,
        "missing": int(missing_count),
        "invalid": int(invalid_count),
        "duplicates": int(duplicate_count),
        "errors": total_errors,
        "quality": quality_score,
        "error_list": error_list[:50]
    }