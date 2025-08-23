import React, { useState } from "react";
import { solve, feedback, randomAnswer } from "../lib/api.js";
import { useEffect } from "react";
import ActionFields from "./ActionFields.jsx"
import BoardHistory from "./BoardHistory.jsx"
import Controls from "./Controls.jsx"


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

            <Controls mode={mode} setMode={setMode} />

            {/* Board (history) */}

            <BoardHistory history={history} input={input} tileClass={tileClass} />

            {/* Actions */}
            <ActionFields
                input={input}
                setInput={setInput}
                onSubmit={submit}
                onSuggest={suggest}
                onReset={handleReset}
            />
        </div>
    );
}


