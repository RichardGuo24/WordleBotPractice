import React, { useEffect, useState, useRef } from "react";
import BoardHistory from "../components/BoardHistory.jsx";              // your 6-row board component
import { feedback, solve, randomAnswer } from "../lib/api.js";

export default function PlayerVsBot()
{
    // shared game state
    const [answer, setAnswer] = useState("");
    const [mode, setMode] = useState("easy");            // "easy" | "hard"
    const [started, setStarted] = useState(false);
    const [finished, setFinished] = useState(false);

    // human
    const [input, setInput] = useState("");
    const [historyHuman, setHistoryHuman] = useState([]); // [{guess, pattern}]

    // bot (kept hidden until finished)
    const [historyBot, setHistoryBot] = useState([]);     // full bot history (guesses/patterns)
    const [botProgress, setBotProgress] = useState(0);    // how many bot rows to gray out
    const botStopRef = useRef(false);                     // cancel flag if round restarts

    // fetch a new answer
    async function seedAnswer()
    {
        const r = await randomAnswer(); // { answer }
        setAnswer(r.answer);
        return r.answer;                // return it so handleStart/runBot can use it
    }

    // start a new race
    async function handleStart()
    {
        botStopRef.current = true;
        await new Promise(r => setTimeout(r, 0)); // let old loop exit
        botStopRef.current = false;

        setFinished(false);
        setHistoryHuman([]);
        setHistoryBot([]);
        setBotProgress(0);
        setInput("");

        try
        {
            const chosen = await seedAnswer();  // ✅ now only one fetch
            setStarted(true);
            runBot(chosen);                     // pass the exact same secret to bot
        } catch (e)
        {
            console.error("Failed to start:", e);
            setStarted(false);
        }
    }

    // human submits a guess
    async function submitHuman()
    {
        const g = input.trim().toLowerCase();
        if (g.length !== 5 || finished || !started) return;

        try
        {
            const { pattern } = await feedback(g, answer);
            const next = [...historyHuman, { guess: g, pattern }];
            setHistoryHuman(next);
            setInput("");

            // win or out of turns?
            const win = pattern === "GGGGG";
            const out = next.length >= 6;
            if (win || out)
            {
                setFinished(true);
            }
        } catch (e)
        {
            console.error("human submit failed:", e);
            alert("Submit failed. Is the server running?");
        }
    }

    // background bot runner (hidden until reveal)
    async function runBot(secret)
    {
        let botHist = [];
        let loops = 0;

        while (!botStopRef.current && loops < 6)
        {
            const s = await solve(botHist, mode, 800); // {nextGuess}
            const g = s.nextGuess;

            const { pattern } = await feedback(g, secret);  // ✅ use the chosen answer
            botHist = [...botHist, { guess: g, pattern }];
            setBotProgress(botHist.length);

            if (pattern === "GGGGG") break;
            loops += 1;
        }

        setHistoryBot(botHist);
    }

    // when the human finishes, reveal bot’s actual guesses after a small delay
    useEffect(() =>
    {
        if (!finished) return;
        // reveal: we’ll just let the bot board render patterns/letters now
    }, [finished]);

    // rendering helpers
    function tileClass(p)
    {
        const base =
            "w-12 h-12 grid place-items-center text-white font-bold rounded-md";
        if (p === "G") return `${base} bg-green-500`;
        if (p === "Y") return `${base} bg-yellow-500`;
        return `${base} bg-gray-700`;
    }

    // a redacted board for the bot: shows gray boxes equal to botProgress while playing,
    // then reveals true history when finished
    function BotBoard()
    {
        if (finished)
        {
            // show true bot board
            return <BoardHistory history={historyBot} input={""} tileClass={tileClass} />;
        }

        // while playing: show botProgress gray rows + remaining empty rows
        const rows = Array.from({ length: 6 }, (_, i) =>
        {
            const isPlayed = i < botProgress;
            const letters = isPlayed ? Array(5).fill(" ") : Array(5).fill(" ");
            return (
                <div key={i} className="flex gap-2 justify-center">
                    {letters.map((_, j) => (
                        <div
                            key={j}
                            className={`w-12 h-12 grid place-items-center font-bold rounded-md
                ${isPlayed ? "bg-gray-500" : "border-2 border-gray-700 text-transparent"}`}
                        >
                            {/* hidden */}
                        </div>
                    ))}
                </div>
            );
        });

        return <div className="mt-6 grid gap-3 justify-center">{rows}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold text-center">Player vs Bot</h1>

            {/* controls */}
            <div className="mt-4 flex items-center justify-center gap-3">
                <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                    disabled={started && !finished}
                    className="border border-gray-300 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="easy">Easy (any valid guess)</option>
                    <option value="hard">Hard (candidates only)</option>
                </select>

                <button
                    onClick={handleStart}
                    disabled={started && !finished}
                    className="rounded-md px-4 py-2 bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50"
                >
                    {started && !finished ? "In Progress…" : "Start"}
                </button>
            </div>

            {/* split screen */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* HUMAN SIDE */}
                <div>
                    <h2 className="text-lg font-semibold text-center mb-2">You</h2>
                    <BoardHistory history={historyHuman} input={input} tileClass={tileClass} />

                    <div className="mt-4 flex gap-2">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value.toLowerCase())}
                            placeholder="your guess"
                            disabled={!started || finished}
                            className="border border-gray-300 rounded-md px-3 py-2 flex-1 outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                        />
                        <button
                            onClick={submitHuman}
                            disabled={!started || finished}
                            className="rounded-md px-3 py-2 bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50"
                        >
                            Submit
                        </button>
                    </div>
                </div>

                {/* BOT SIDE */}
                <div>
                    <h2 className="text-lg font-semibold text-center mb-2">Bot</h2>
                    <BotBoard />
                    {!finished && started && (
                        <p className="text-center text-sm text-gray-400 mt-2">
                            Bot is guessing… rows will reveal after you finish.
                        </p>
                    )}
                    {finished && (
                        <p className="text-center text-sm text-gray-600 mt-2">
                            Revealed! Bot took {historyBot.length} guess{historyBot.length === 1 ? "" : "es"}.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
