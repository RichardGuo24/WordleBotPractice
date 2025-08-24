from collections import Counter
from functools import lru_cache
import random

# If you already have these modules, keep them; otherwise stub them or load from files.
from wordle_secret_words import get_secret_words
from valid_wordle_guesses import get_valid_wordle_guesses

# Normalize lists to lowercase 5-letter words
VALID = {w.strip().lower() for w in get_valid_wordle_guesses() if len(w) == 5 and w.isalpha()}
ANSWERS = {w.strip().lower() for w in get_secret_words()         if len(w) == 5 and w.isalpha()}

@lru_cache(maxsize=500_000)
def feedback_pattern(guess: str, answer: str) -> str:
    g = guess.lower()
    a = answer.lower()
    res = ['B'] * 5

    # count non-green letters in answer
    counts = [0]*26
    ai = lambda ch: ord(ch) - 97

    # mark greens & tally remaining answer letters
    for i, ch in enumerate(g):
        if ch == a[i]:
            res[i] = 'G'
        else:
            counts[ai(a[i])] += 1

    # mark yellows using counts
    for i, ch in enumerate(g):
        if res[i] == 'G': 
            continue
        idx = ai(ch)
        if counts[idx] > 0:
            res[i] = 'Y'
            counts[idx] -= 1

    return ''.join(res)

def filter_candidates(cands: set[str], guess: str, pattern: str) -> set[str]:
    """Keep only words that would yield 'pattern' when 'guess' is compared to them."""
    return {w for w in cands if feedback_pattern(guess, w) == pattern}

def expected_remaining(guess: str, cands: list[str], cap: int = 600) -> float:
    """Lower is better: expected size of the candidate set after playing 'guess'."""
    n = len(cands)
    if n == 0:
        return 0.0

    # 1) SAMPLE candidates to bound work
    sample = cands if n <= cap else random.sample(cands, cap)
    m = len(sample)

    # 2) Build buckets on the sample (fast)
    buckets = Counter(feedback_pattern(guess, w) for w in sample)

    # 3) SCALE the expectation back to the full set size
    #    If a pattern is a fraction p = cnt/m of the sample,
    #    we estimate it would be p*n in the full set.
    #    Expected remaining ≈ Σ p * (p*n) over buckets.
    return sum((cnt / m) * (cnt * (n / m)) for cnt in buckets.values())

def pick_best_guess(cands: set[str],
                    valid_guesses: set[str],
                    easy_mode: bool = True,
                    sample_limit: int = 300) -> str:
    if len(cands) == 1:
        return next(iter(cands))

    # cap the guess pool; scale with problem size
    if easy_mode:
        pool = set(valid_guesses)
        limit = min(sample_limit, max(100, len(cands) // 2))
        if len(pool) > limit:
            pool = set(random.sample(list(pool), limit))
        pool |= cands
    else:
        pool = set(cands)

    c_list = list(cands)

    # pre-sample candidates ONCE; reuse for all guesses (stable & fast)
    cand_cap = 600 if len(c_list) > 600 else len(c_list)
    c_eval = c_list if len(c_list) <= cand_cap else random.sample(c_list, cand_cap)

    best_g, best_s = None, float('inf')
    for g in pool:
        s = expected_remaining(g, c_eval, cap=cand_cap)  # score on subset
        if s < best_s or (s == best_s and g in cands):
            best_g, best_s = g, s
    return best_g or next(iter(cands))

def start_candidates() -> set[str]:
    """Fresh candidate set at the start of a game."""
    return set(ANSWERS)

def is_valid_guess(w: str) -> bool:
    return w.lower() in VALID