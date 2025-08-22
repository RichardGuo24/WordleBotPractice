from flask import Flask, request, jsonify
from flask_cors import CORS
from solver import (
    feedback_pattern, filter_candidates, pick_best_guess,
    start_candidates, is_valid_guess, VALID
)

app = Flask(__name__)
# Needed in local dev because web runs at :5173 and server at :5001 (different origins)
CORS(app)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/feedback")
def api_feedback():
    data = request.get_json(force=True)
    guess = (data.get("guess") or "").lower().strip()
    answer = (data.get("answer") or "").lower().strip()

    if len(guess) != 5 or len(answer) != 5 or not guess.isalpha() or not answer.isalpha():
        return jsonify({"error": "guess and answer must be 5 letters (a-z)"}), 400

    return jsonify({"pattern": feedback_pattern(guess, answer)})

@app.post("/solve")
def api_solve():
    """
    Request JSON:
      {
        "history": [{"guess":"slate","pattern":"BBYBB"}, ...],
        "mode": "easy" | "hard",
        "sample": 800
      }
    Response JSON:
      {
        "nextGuess": "cabin",
        "candidates": 42,
        "expectedRemaining": 7.8
      }
    """
    data = request.get_json(force=True)
    history = data.get("history", [])
    mode = (data.get("mode") or "easy").lower()
    sample = int(data.get("sample", 800))

    # rebuild candidates from scratch based on history
    cands = start_candidates()
    try:
        for h in history:
            g = (h["guess"]).lower().strip()
            p = h["pattern"]
            cands = filter_candidates(cands, g, p)
    except Exception:
        return jsonify({"error": "Malformed history items"}), 400

    if not cands:
        return jsonify({"error": "No candidates remain (history inconsistent?)"}), 400

    easy_mode = (mode == "easy")
    guess = pick_best_guess(cands, VALID, easy_mode=easy_mode, sample_limit=sample)

    # Optional: compute expected remaining for UI
    from collections import Counter
    c_list = list(cands)
    n = len(c_list)
    buckets = Counter(feedback_pattern(guess, w) for w in c_list)
    expected = sum((cnt / n) * cnt for cnt in buckets.values()) if n else 0.0

    return jsonify({
        "nextGuess": guess,
        "candidates": len(cands),
        "expectedRemaining": expected
    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)
