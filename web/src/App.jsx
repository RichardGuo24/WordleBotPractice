import { BrowserRouter, Routes, Route } from "react-router-dom"
import Header from "./Header.jsx"
import Home from "./Home.jsx"
import PlayerVsBot from "./PlayerVsBot.jsx"



export default function App()
{
    return (
        <BrowserRouter>
            <Header />
            <Routes>
                <Route path="/" element={<Home />}></Route>
                <Route path="/playervsbot" element={<PlayerVsBot />}></Route>
            </Routes>

        </BrowserRouter>
    )
}