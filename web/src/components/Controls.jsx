export default function Controls({ mode, setMode })
{
    return (
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
    )

}