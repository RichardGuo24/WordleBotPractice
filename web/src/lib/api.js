const BASE = import.meta.env.VITE_API_URL || "http://localhost:5001";

export async function solve(history, mode = "easy", sample = 800)
{
    const r = await fetch(`${BASE}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history, mode, sample })
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json(); // { nextGuess, candidates, expectedRemaining }
}

export async function feedback(guess, answer)
{
    const r = await fetch(`${BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ guess, answer })
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json(); // { pattern }
}


export async function randomAnswer()
{
    const r = await fetch(`${BASE}/random_answer`)
    if (!r)
    {
        throw new Error(await r.text())
    }
    return r.json();
}