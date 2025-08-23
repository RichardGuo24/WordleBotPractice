export default function ActionFields
    ({
        input,
        setInput,
        onSubmit,
        onSuggest,
        onReset,
        disabled = false,
    })
{
    // allow Enter key to submit
    function handleKeyDown(e)
    {
        if (e.key === "Enter")
        {
            e.preventDefault();
            onSubmit?.();
        }
    }

    return (
        <div className="mt-4 flex gap-2">
            <input
                value={input}
                onChange={(e) => setInput(e.target.value.toLowerCase())}
                onKeyDown={handleKeyDown}
                placeholder="your guess"
                className="border border-gray-300 rounded-md px-3 py-2 flex-1 outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={disabled}
                aria-label="Your guess"
            />

            <button
                onClick={onSubmit}
                disabled={disabled}
                className="rounded-md px-3 py-2 bg-indigo-600 text-white font-medium hover:bg-indigo-700 active:bg-indigo-800 disabled:opacity-50"
            >
                Submit
            </button>

            <button
                onClick={onSuggest}
                disabled={disabled}
                className="rounded-md px-3 py-2 bg-slate-700 text-white font-medium hover:bg-slate-800 active:bg-slate-900 disabled:opacity-50"
            >
                Suggest
            </button>

            <button
                onClick={onReset}
                disabled={disabled}
                className="rounded-md px-3 py-2 border border-gray-300 text-white hover:bg-gray-100 bg-green-600 disabled:opacity-50"
            >
                🎲 Reset / Randomize
            </button>
        </div>
    );
}