from collections import Counter
import random

# If you already have these modules, keep them; otherwise stub them or load from files.
from wordle_secret_words import get_secret_words
from valid_wordle_guesses import get_valid_wordle_guesses

# Normalize lists to lowercase 5-letter words
VALID = {w.strip().lower() for w in get_valid_wordle_guesses() if len(w) == 5 and w.isalpha()}
ANSWERS = {w.strip().lower() for w in get_secret_words()         if len(w) == 5 and w.isalpha()}

def feedback_pattern(guess: str, answer: str) -> str:
    """
    Return a 5-char string of G/Y/B for guess vs answer, matching Wordle rules.
    """
    g, a = guess.lower(), answer.lower()
    res = ['B'] * 5
    rem = list(a)

    # mark greens
    for i, ch in enumerate(g):
        if ch == a[i]:
            res[i] = 'G'
            rem[i] = None

    # mark yellows
    for i, ch in enumerate(g):
        if res[i] == 'B' and ch in rem:
            res[i] = 'Y'
            rem[rem.index(ch)] = None

    return ''.join(res)

def filter_candidates(cands: set[str], guess: str, pattern: str) -> set[str]:
    """Keep only words that would yield 'pattern' when 'guess' is compared to them."""
    return {w for w in cands if feedback_pattern(guess, w) == pattern}

def expected_remaining(guess: str, cands: list[str]) -> float:
    """Lower is better: expected size of the candidate set after playing 'guess'."""
    n = len(cands)
    if n == 0:
        return 0.0
    buckets = Counter(feedback_pattern(guess, w) for w in cands)
    return sum((cnt / n) * cnt for cnt in buckets.values())

def pick_best_guess(cands: set[str],
                    valid_guesses: set[str],
                    easy_mode: bool = True,
                    sample_limit: int = 300) -> str:
    """
    Choose next guess.
    - easy_mode=True: consider any valid guess (better splitting)
    - always include candidates; if single candidate, return it immediately
    """
    if len(cands) == 1:
        return next(iter(cands))

    if easy_mode:
        pool = set(valid_guesses)
        if len(pool) > sample_limit:
            pool = set(random.sample(list(pool), sample_limit))
        pool |= cands  # always include candidates
    else:
        pool = set(cands)

    c_list = list(cands)
    best_g, best_s = None, float('inf')
    for g in pool:
        s = expected_remaining(g, c_list)
        if s < best_s or (s == best_s and g in cands):
            best_g, best_s = g, s
    return best_g or next(iter(cands))

def start_candidates() -> set[str]:
    """Fresh candidate set at the start of a game."""
    return set(ANSWERS)

def is_valid_guess(w: str) -> bool:
    return w.lower() in VALID