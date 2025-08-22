import React, { useState } from "react";
import { solve, feedback } from "./lib/api.js";

export default function App()
{
    const [answer, setAnswer] = useState("");         // local practice answer
    const [history, setHistory] = useState([]);       // [{guess, pattern}]
    const [input, setInput] = useState("");
    const [mode, setMode] = useState("easy");         // "easy" | "hard"

    async function submit()
    {
        const g = input.trim().toLowerCase();
        if (g.length !== 5) return;
        const { pattern } = await feedback(g, answer.trim().toLowerCase());
        setHistory(h => [...h, { guess: g, pattern }]);
        setInput("");
    }

    async function suggest()
    {
        const resp = await solve(history, mode, 800);
        setInput(resp.nextGuess);
    }

    function tileClass(p)
    {
        // base tile styles + color by pattern
        const base =
            "w-12 h-12 grid place-items-center text-white font-bold rounded-md";
        if (p === "G") return `${base} bg-green-500`;
        if (p === "Y") return `${base} bg-yellow-500`;
        return `${base} bg-gray-700`;
    }

    return (
        <div className="max-w-xl mx-auto mt-10 font-sans px-4">
            <h1 className="text-2xl font-bold text-center">Wordle Practice / Bot</h1>

            {/* Controls */}
            <div className="mt-4 flex items-center gap-2">
                <input
                    placeholder="secret answer (practice)"
                    value={answer}
                    onChange={e => setAnswer(e.target.value.toLowerCase())}
                    className="border border-gray-300 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <select
                    value={mode}
                    onChange={e => setMode(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="easy">easy (any valid guess)</option>
                    <option value="hard">hard (candidates only)</option>
                </select>
            </div>

            {/* Board (history) */}
            <div className="mt-4 grid gap-2">
                {history.map((h, i) => (
                    <div key={i} className="flex gap-2">
                        {h.guess.toUpperCase().split("").map((ch, j) => (
                            <div key={j} className={tileClass(h.pattern[j])}>
                                {ch}
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Actions */}
            <div className="mt-4 flex gap-2">
                <input
                    value={input}
                    onChange={e => setInput(e.target.value.toLowerCase())}
                    placeholder="your guess"
                    className="border border-gray-300 rounded-md px-3 py-2 flex-1 outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                    onClick={submit}
                    className="rounded-md px-3 py-2 bg-indigo-600 text-white font-medium hover:bg-indigo-700 active:bg-indigo-800"
                >
                    Submit
                </button>
                <button
                    onClick={suggest}
                    className="rounded-md px-3 py-2 bg-slate-700 text-white font-medium hover:bg-slate-800 active:bg-slate-900"
                >
                    Suggest
                </button>
                <button
                    onClick={() => setHistory([])}
                    className="rounded-md px-3 py-2 border border-gray-300 text-gray-700 hover:bg-gray-100"
                >
                    Reset
                </button>
            </div>
        </div>
    );
}
