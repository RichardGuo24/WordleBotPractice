import React, { useState } from "react";
import { solve, feedback, randomAnswer } from "./lib/api.js";
import { useEffect } from "react";

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

    async function handleReset()
    {
        setHistory([]);
        try
        {
            const { answer: a } = await randomAnswer();
            setAnswer(a);
        } catch (err)
        {
            console.error("Failed to fetch random answer", err);
        }
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

    useEffect(() =>
    {
        async function fetchAnswer()
        {
            try
            {
                const { answer } = await randomAnswer();
                setAnswer(answer);
            } catch (err)
            {
                console.error("Failed to fetch random answer", err);
            }
        }
        fetchAnswer();
    }, []);

    return (
        <div className="max-w-2xl mx-auto mt-10 font-sans px-4">
            <h1 className="text-5xl font-light text-center">Wordle Practice</h1>

            {/* Controls */}
            <div className="mt-4 flex items-center justify-center gap-2">
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


            <div className="mt-4 grid gap-3 justify-center">
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
                    onClick={() => handleReset()}
                    className="rounded-md px-3 py-2 border border-gray-300 text-white hover:bg-gray-100 bg-green-600"
                >
                    🎲 Reset / Randomize
                </button>
            </div>
        </div>
    );
}
