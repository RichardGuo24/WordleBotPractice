import React from "react";

/**
 * Props:
 *  - history: [{ guess: "slate", pattern: "BBYBB" }, ...]
 *  - input:   current input string (e.g., "po")
 *  - tileClass: (p: "G"|"Y"|"B") => string of Tailwind classes
 */
export default function Board({ history, input, tileClass })
{
    return (
        <div className="mt-6 grid gap-3 justify-center">
            {Array.from({ length: 6 }, (_, i) =>
            {
                const played = history[i];           // completed guess at this row (if any)
                const isNext = i === history.length; // the row the player is typing in now

                // Always produce 5 “letters” to render as tiles
                const letters = played
                    ? played.guess.toUpperCase().split("")
                    : isNext
                        ? (input.toUpperCase().padEnd(5, " ").slice(0, 5)).split("")
                        : Array(5).fill(" ");

                return (
                    <div key={i} className="flex gap-2 justify-center">
                        {letters.map((ch, j) =>
                        {
                            if (played)
                            {
                                // Completed guess → colored tiles from pattern
                                return (
                                    <div key={j} className={tileClass(played.pattern[j])}>
                                        {ch}
                                    </div>
                                );
                            }

                            // In-progress row vs future empty rows (outlined tiles)
                            const base = "w-12 h-12 grid place-items-center font-bold rounded-md";
                            const inProgress = "border-2 border-gray-500 text-white";
                            const emptyFuture = "border-2 border-gray-700 text-transparent";

                            return (
                                <div
                                    key={j}
                                    className={`${base} ${isNext ? inProgress : emptyFuture}`}
                                >
                                    {ch}
                                </div>
                            );
                        })}
                    </div>
                );
            })}
        </div>
    );
}