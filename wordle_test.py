from __future__ import annotations
from collections import Counter
from functools import lru_cache
import argparse
import random
from typing import Iterable, List, Set, Tuple

try:
    from colorama import Fore, Back, Style, init as colorama_init
    colorama_init(autoreset=True)
    _HAS_COLOR = True
except Exception:
    _HAS_COLOR = False

# ---- Load word lists (keep everything lowercase) ---------------------------

def load_word_sets() -> Tuple[Set[str], Set[str]]:
    """Return (valid_guesses, answers) as lowercase sets."""
    from wordle_secret_words import get_secret_words
    from valid_wordle_guesses import get_valid_wordle_guesses
    valid = set(w.strip().lower() for w in get_valid_wordle_guesses())
    answers = set(w.strip().lower() for w in get_secret_words())
    # Some lists include the answer set within valid list; that's fine.
    # Ensure 5-letter alphabetic words only.
    valid = {w for w in valid if len(w) == 5 and w.isalpha()}
    answers = {w for w in answers if len(w) == 5 and w.isalpha()}
    return valid, answers

# ---- Feedback --------------------------------------------------------------

@lru_cache(maxsize=1_000_000)
def feedback_pattern(guess: str, answer: str) -> str:
    """
    Compute Wordle feedback between guess and answer, returning a 5-char string in {G,Y,B}.
    G = green (correct letter, correct position)
    Y = yellow (in word, wrong position)
    B = gray/black (not in word, or already consumed by G/Y elsewhere)
    
    """
    g = guess.lower()
    a = answer.lower()
    if len(g) != 5 or len(a) != 5:
        raise ValueError("Guess and answer must be length 5")

    res = ['B'] * 5
    rem = list(a)

    # Greens
    for i, ch in enumerate(g):
        if ch == a[i]:
            res[i] = 'G'
            rem[i] = None

    # Yellows
    for i, ch in enumerate(g):
        if res[i] == 'B' and ch in rem:
            res[i] = 'Y'
            # consume the first available instance
            rem[rem.index(ch)] = None

    return ''.join(res)

# ---- Candidate maintenance --------------------------------------------------

def filter_candidates(cands: Set[str], g: str, p: str) -> Set[str]:
    """Keep only words that would produce pattern p for guess g."""
    return {w for w in cands if feedback_pattern(g, w) == p}

# ---- Scoring (information gain-ish) ----------------------------------------

def expected_remaining(guess: str, cands: Iterable[str]) -> float:
    """
    Lower is better: sum_p (|Bp|/|S|) * |Bp|, where Bp is the bucket of candidates
    yielding pattern p for 'guess', and S is the current candidate set.
    """
    cands_list = list(cands)
    n = len(cands_list)
    if n == 0:
        return 0.0
    buckets = Counter(feedback_pattern(guess, w) for w in cands_list)
    return sum((cnt / n) * cnt for cnt in buckets.values())

def pick_best_guess(
    cands: Set[str],
    valid_guesses: Set[str],
    easy_mode: bool = True,
    sample_limit: int = 1000,
) -> Tuple[str, float]:
    # If there’s only one candidate, return it immediately.
    if len(cands) == 1:
        only = next(iter(cands))
        return only, 0.0

    if easy_mode:
        # Start from the full valid-guess pool…
        pool = set(valid_guesses)
        # …optionally sample for speed…
        if len(pool) > sample_limit:
            pool = set(random.sample(list(pool), sample_limit))
        # …but ALWAYS include all current candidates so we never miss them.
        pool |= cands
    else:
        # Hard mode just considers the candidates.
        pool = set(cands)

    cands_list = list(cands)
    best_g, best_s = None, float('inf')

    for g in pool:
        s = expected_remaining(g, cands_list)
        # Tie-break: prefer guesses that are in the candidate set
        if s < best_s or (s == best_s and g in cands):
            best_g, best_s = g, s

    if best_g is None:
        # Extremely defensive fallback
        best_g = next(iter(cands))
        best_s = expected_remaining(best_g, cands_list)
    return best_g, best_s
# ---- Pretty printing --------------------------------------------------------

def colorize(guess: str, pattern: str) -> str:
    if not _HAS_COLOR:
        # fallback: [G]letters, (Y)letters, -gray
        out = []
        for ch, p in zip(guess.upper(), pattern):
            if p == 'G':
                out.append(f"[{ch}]")
            elif p == 'Y':
                out.append(f"({ch})")
            else:
                out.append(f"-{ch}-")
        return " ".join(out)

    # Colorama backgrounds if available
    blocks = []
    for ch, p in zip(guess.upper(), pattern):
        if p == 'G':
            blocks.append(Back.GREEN + ch)
        elif p == 'Y':
            blocks.append(Back.YELLOW + ch)
        else:
            blocks.append(Back.BLACK + ch)
    return "".join(blocks)

# ---- Game loops -------------------------------------------------------------

def solve_one(
    answer: str,
    valid_guesses: Set[str],
    answers: Set[str],
    opener: str = "slate",
    easy_mode: bool = True,
    max_turns: int = 6,
    sample_limit: int = 1000,
    verbose: bool = True,
) -> Tuple[bool, int, List[Tuple[str, str]]]:
    """
    Solve a single game for a given 'answer'. Returns (won, turns_used, history).
    history is a list of (guess, pattern).
    """
    ans = answer.lower()
    if ans not in answers:
        # Allow solving any 5-letter word—just warn if it's not in answer list
        if verbose:
            print(f"[warn] '{answer}' not in official answer set; still attempting.")

    cands = set(answers)  # per-game candidate set
    history: List[Tuple[str, str]] = []

    for turn in range(max_turns):
        if turn == 0 and opener:
            guess = opener
        elif len(cands) == 1:
            # Only one possible answer left — take it.
            guess = next(iter(cands))
        else:
            guess, _ = pick_best_guess(
                cands,
                valid_guesses,
                easy_mode=easy_mode,
                sample_limit=sample_limit
            )

        pat = feedback_pattern(guess, ans)
        history.append((guess, pat))

        if verbose:
            print(f"Turn {turn+1}: {colorize(guess, pat)}   ({len(cands)} candidates before)")

        if pat == "GGGGG":
            return True, turn + 1, history

        # shrink candidate set
        cands = filter_candidates(cands, guess, pat)
        if not cands:
            # dead end (inconsistent history or off-list answer)
            return False, turn + 1, history

    return False, max_turns, history

def eval_all(
    valid_guesses: Set[str],
    answers: Set[str],
    opener: str = "slate",
    easy_mode: bool = True,
    max_turns: int = 6,
    sample_limit: int = 1000,
    limit: int | None = None,
) -> Tuple[int, int, float]:
    """
    Evaluate performance over many answers (optionally sample with 'limit').
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
            opener=opener, easy_mode=easy_mode,
            max_turns=max_turns, sample_limit=sample_limit, verbose=False
        )
        wins += int(won)
        losses += int(not won)
        total_guesses += turns
        if i % 50 == 0:
            print(f"… evaluated {i}/{len(pool)}")

    avg = total_guesses / max(1, (wins + losses))
    return wins, losses, avg

# ---- CLI --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Wordle solver (information-theoretic).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    play = sub.add_parser("play", help="Solve a single answer word.")
    play.add_argument("answer", type=str, help="The secret/answer word to solve.")
    play.add_argument("--opener", default="slate")
    play.add_argument("--hard", action="store_true", help="Hard mode (restrict guesses to candidates).")
    play.add_argument("--turns", type=int, default=6)
    play.add_argument("--sample", type=int, default=1000, help="Sample size for guess scoring.")
    play.add_argument("--quiet", action="store_true")

    bench = sub.add_parser("bench", help="Evaluate over many answers.")
    bench.add_argument("--limit", type=int, default=None, help="Number of answers to sample for the benchmark.")
    bench.add_argument("--opener", default="slate")
    bench.add_argument("--hard", action="store_true")
    bench.add_argument("--turns", type=int, default=6)
    bench.add_argument("--sample", type=int, default=1000)

    args = parser.parse_args()
    valid, answers = load_word_sets()

    if args.cmd == "play":
        won, turns, history = solve_one(
            args.answer, valid, answers,
            opener=args.opener,
            easy_mode=not args.hard,
            max_turns=args.turns,
            sample_limit=args.sample,
            verbose=not args.quiet
        )
        if not args.quiet:
            print("\nResult:", "WIN" if won else "LOSS", f"in {turns} turn(s)")
            for g, p in history:
                print(f"  {g}  {p}")

    elif args.cmd == "bench":
        wins, losses, avg = eval_all(
            valid, answers,
            opener=args.opener,
            easy_mode=not args.hard,
            max_turns=args.turns,
            sample_limit=args.sample,
            limit=args.limit
        )
        total = wins + losses
        print(f"Played: {total} | Wins: {wins} | Losses: {losses} | Avg guesses: {avg:.3f}")

if __name__ == "__main__":
    main()
