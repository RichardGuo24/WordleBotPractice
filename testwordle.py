#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from typing import Iterable, List, Set, Tuple, Optional
import argparse
import random
import os

# Optional colors for pretty printing in "play" mode
try:
    from colorama import Fore, Back, Style, init as colorama_init
    colorama_init(autoreset=True)
    _HAS_COLOR = True
except Exception:
    _HAS_COLOR = False

# =============================================================================
# Word lists
# =============================================================================

def load_word_sets() -> Tuple[Set[str], Set[str]]:
    """
    Return (valid_guesses, answers) as lowercase sets (5-letter alphabetic).
    Expects two helper modules in the same directory:
      - wordle_secret_words.get_secret_words()
      - valid_wordle_guesses.get_valid_wordle_guesses()
    """
    from wordle_secret_words import get_secret_words
    from valid_wordle_guesses import get_valid_wordle_guesses

    valid = set(w.strip().lower() for w in get_valid_wordle_guesses())
    answers = set(w.strip().lower() for w in get_secret_words())
    valid = {w for w in valid if len(w) == 5 and w.isalpha()}
    answers = {w for w in answers if len(w) == 5 and w.isalpha()}
    return valid, answers


# =============================================================================
# Feedback (optimized + cached)
# =============================================================================

@lru_cache(maxsize=1_000_000)
def feedback_pattern(guess: str, answer: str) -> str:
    """
    Compute Wordle feedback (G/Y/B) between guess and answer.
    Optimized: two-pass counting with O(1) per letter operations + LRU cache.
    """
    g = guess.lower()
    a = answer.lower()
    if len(g) != 5 or len(a) != 5:
        raise ValueError("Guess and answer must be length 5")

    res = ['B'] * 5

    # Count remaining letters of 'answer' that weren't green
    counts = [0] * 26
    ai = lambda ch: ord(ch) - 97  # 'a' -> 0 ... 'z' -> 25

    # Pass 1: mark greens, tally non-green letters from answer
    for i, ch in enumerate(g):
        if ch == a[i]:
            res[i] = 'G'
        else:
            counts[ai(a[i])] += 1

    # Pass 2: mark yellows where counts allow
    for i, ch in enumerate(g):
        if res[i] == 'G':
            continue
        idx = ai(ch)
        if 0 <= idx < 26 and counts[idx] > 0:
            res[i] = 'Y'
            counts[idx] -= 1

    return ''.join(res)


# =============================================================================
# Candidate maintenance
# =============================================================================

def filter_candidates(cands: Set[str], guess: str, pattern: str) -> Set[str]:
    """Keep only words that would produce 'pattern' for 'guess'."""
    return {w for w in cands if feedback_pattern(guess, w) == pattern}


# =============================================================================
# Scoring (sampled expected remaining)
# =============================================================================

def expected_remaining(guess: str,
                       cands: Iterable[str],
                       cand_cap: Optional[int] = 600) -> float:
    """
    Estimate expected remaining candidates after playing 'guess'.
    If cand_cap is None or 0, compute EXACT over all candidates.
    Otherwise, sample up to 'cand_cap' candidates and scale.

    Returns: approx n * sum_buckets (p_b^2), where p_b are pattern proportions.
    Lower is better.
    """
    c_list = list(cands)
    n = len(c_list)
    if n == 0:
        return 0.0

    if not cand_cap or n <= cand_cap:
        # Exact buckets
        buckets = Counter(feedback_pattern(guess, w) for w in c_list)
        return sum((cnt / n) * cnt for cnt in buckets.values())

    # Sample for speed, then scale back to n via proportions
    sample = random.sample(c_list, cand_cap)
    m = len(sample)
    buckets = Counter(feedback_pattern(guess, w) for w in sample)
    # E ≈ n * Σ ( (cnt/m)^2 )
    return n * sum((cnt / m) * (cnt / m) for cnt in buckets.values())


def pick_best_guess(cands: Set[str],
                    valid_guesses: Set[str],
                    easy_mode: bool = True,
                    guess_pool_limit: int = 300,
                    cand_cap: Optional[int] = 600) -> Tuple[str, float]:
    """
    Choose the next guess quickly:
      - Limit the GUESS POOL size (adaptive, always includes cands)
      - Score guesses against a SHARED subset of candidates (cand_cap)
      - Tie-break toward guesses that are in the candidate set
    Returns: (best_guess, score_estimate)
    """
    if len(cands) == 1:
        only = next(iter(cands))
        return only, 0.0

    # Build guess pool
    if easy_mode:
        pool = set(valid_guesses)
        # Adaptive pool limit scales with search size; never below 100.
        adaptive_limit = min(guess_pool_limit, max(100, len(cands) // 2))
        if len(pool) > adaptive_limit:
            pool = set(random.sample(list(pool), adaptive_limit))
        pool |= cands  # always include candidates
    else:
        pool = set(cands)

    c_list = list(cands)

    # Pre-sample candidates ONCE for stable, fair comparisons
    if not cand_cap or len(c_list) <= cand_cap:
        c_eval = c_list  # exact mode or already small
        eff_cap = None if not cand_cap else cand_cap
    else:
        c_eval = random.sample(c_list, cand_cap)
        eff_cap = cand_cap

    best_g, best_s = None, float('inf')
    for g in pool:
        s = expected_remaining(g, c_eval, cand_cap=eff_cap)
        if s < best_s or (s == best_s and g in cands):
            best_g, best_s = g, s

    if best_g is None:
        best_g = next(iter(cands))
        best_s = expected_remaining(best_g, c_eval, cand_cap=eff_cap)
    return best_g, best_s


# =============================================================================
# Pretty printing
# =============================================================================

def colorize(guess: str, pattern: str) -> str:
    if not _HAS_COLOR:
        out = []
        for ch, p in zip(guess.upper(), pattern):
            if p == 'G':
                out.append(f"[{ch}]")
            elif p == 'Y':
                out.append(f"({ch})")
            else:
                out.append(f"-{ch}-")
        return " ".join(out)

    blocks = []
    for ch, p in zip(guess.upper(), pattern):
        if p == 'G':
            blocks.append(Back.GREEN + ch)
        elif p == 'Y':
            blocks.append(Back.YELLOW + ch)
        else:
            blocks.append(Back.BLACK + ch)
    return "".join(blocks)


# =============================================================================
# Game loops
# =============================================================================

def solve_one(answer: str,
              valid_guesses: Set[str],
              answers: Set[str],
              opener: Optional[str] = "raise",
              easy_mode: bool = True,
              max_turns: int = 6,
              guess_pool_limit: int = 300,
              cand_cap: Optional[int] = 600,
              verbose: bool = True) -> Tuple[bool, int, List[Tuple[str, str]]]:
    """
    Solve a single game for a given 'answer'. Returns (won, turns_used, history).
    history is a list of (guess, pattern).
    - opener: fixed first guess (fast path). Set to ""/None to compute first move.
    - cand_cap: None/0 means exact scoring; otherwise sampled with this cap.
    """
    ans = answer.lower()
    if ans not in answers and verbose:
        print(f"[warn] '{answer}' not in official answer set; still attempting.")

    cands = set(answers)
    history: List[Tuple[str, str]] = []

    for turn in range(max_turns):
        if turn == 0 and opener:
            guess = opener
        elif len(cands) == 1:
            guess = next(iter(cands))
        else:
            # Hybrid: once the set is small, switch to exact automatically
            dynamic_cap = (None if (cand_cap is None or cand_cap == 0 or len(cands) <= 600)
                           else cand_cap)
            # If small, also allow a bigger guess pool
            dynamic_pool = guess_pool_limit if len(cands) > 600 else max(guess_pool_limit, 500)
            guess, _ = pick_best_guess(
                cands,
                valid_guesses,
                easy_mode=easy_mode,
                guess_pool_limit=dynamic_pool,
                cand_cap=dynamic_cap
            )

        pat = feedback_pattern(guess, ans)
        history.append((guess, pat))

        if verbose:
            print(f"Turn {turn+1}: {colorize(guess, pat)}   ({len(cands)} candidates before)")

        if pat == "GGGGG":
            return True, turn + 1, history

        cands = filter_candidates(cands, guess, pat)
        if not cands:
            return False, turn + 1, history

    return False, max_turns, history


def eval_all(valid_guesses: Set[str],
             answers: Set[str],
             opener: Optional[str] = "raise",
             easy_mode: bool = True,
             max_turns: int = 6,
             guess_pool_limit: int = 300,
             cand_cap: Optional[int] = 600,
             limit: int | None = None) -> Tuple[int, int, float]:
    """
    Evaluate performance over many answers (optionally a random 'limit').
    Returns (wins, losses, average_guesses_over_played).
    """
    pool = list(answers)
    random.shuffle(pool)
    if limit is not None:
        pool = pool[:limit]

    wins = 0
    losses = 0
    total_guesses = 0

    for i, ans in enumerate(pool, 1):
        won, turns, _ = solve_one(
            ans, valid_guesses, answers,
            opener=opener,
            easy_mode=easy_mode,
            max_turns=max_turns,
            guess_pool_limit=guess_pool_limit,
            cand_cap=cand_cap,
            verbose=False
        )
        wins += int(won)
        losses += int(not won)
        total_guesses += turns
        if i % 50 == 0:
            print(f"… evaluated {i}/{len(pool)}")

    avg = total_guesses / max(1, (wins + losses))
    return wins, losses, avg


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Wordle solver (fast, sampled scoring).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    play = sub.add_parser("play", help="Solve a single answer word.")
    play.add_argument("answer", type=str, help="The secret/answer word to solve.")
    play.add_argument("--opener", default=os.environ.get("DEFAULT_FIRST_GUESS", "raise"),
                      help="Fixed first guess (default: %(default)s). Use '' to compute first move.")
    play.add_argument("--hard", action="store_true", help="Hard mode (restrict guesses to candidates).")
    play.add_argument("--turns", type=int, default=6)
    play.add_argument("--guess-pool", type=int, default=300,
                      help="Max number of guesses to score (adaptive, min 100).")
    play.add_argument("--cand-cap", type=int, default=600,
                      help="Max candidates to score against (None/0 = exact).")
    play.add_argument("--seed", type=int, default=None, help="Random seed for reproducible sampling.")
    play.add_argument("--quiet", action="store_true")

    bench = sub.add_parser("bench", help="Evaluate over many answers.")
    bench.add_argument("--limit", type=int, default=None, help="Number of answers to sample for the benchmark.")
    bench.add_argument("--opener", default=os.environ.get("DEFAULT_FIRST_GUESS", "raise"))
    bench.add_argument("--hard", action="store_true")
    bench.add_argument("--turns", type=int, default=6)
    bench.add_argument("--guess-pool", type=int, default=300)
    bench.add_argument("--cand-cap", type=int, default=600)
    bench.add_argument("--seed", type=int, default=None)

    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    valid, answers = load_word_sets()

    if args.cmd == "play":
        opener_arg = args.opener if args.opener != "" else None
        won, turns, history = solve_one(
            args.answer, valid, answers,
            opener=opener_arg,
            easy_mode=not args.hard,
            max_turns=args.turns,
            guess_pool_limit=args.guess_pool,
            cand_cap=(None if args.cand_cap in (None, 0) else args.cand_cap),
            verbose=not args.quiet
        )
        if not args.quiet:
            print("\nResult:", "WIN" if won else "LOSS", f"in {turns} turn(s)")
            for g, p in history:
                print(f"  {g}  {p}")

    elif args.cmd == "bench":
        wins, losses, avg = eval_all(
            valid, answers,
            opener=(args.opener if args.opener != "" else None),
            easy_mode=not args.hard,
            max_turns=args.turns,
            guess_pool_limit=args.guess_pool,
            cand_cap=(None if args.cand_cap in (None, 0) else args.cand_cap),
            limit=args.limit
        )
        total = wins + losses
        print(f"Played: {total} | Wins: {wins} | Losses: {losses} | Avg guesses: {avg:.3f}")


if __name__ == "__main__":
    main()
