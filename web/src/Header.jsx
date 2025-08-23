import { Link } from "react-router-dom"

export default function Header()
{

    return (
        <nav className="h-25 mr-8 flex justify-end items-center gap-7">

            <Link to="/" className="text-xl">Practice</Link>
            <Link to="/playervsbot" className="text-xl">Player vs Bot</Link>

        </nav>
    )

}