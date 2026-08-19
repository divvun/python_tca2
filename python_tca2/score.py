from fractions import Fraction

Score = Fraction


def as_score(value: int | float | str | Score) -> Score:
    """Create an exact score from a decimal constant or integer."""
    if isinstance(value, Score):
        return value
    return Score(str(value))