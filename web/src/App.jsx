import { BrowserRouter, Routes, Route } from "react-router-dom"
import Header from "./components/Header.jsx"
import Home from "./components/Home.jsx"
import PlayerVsBot from "./components/PlayerVsBot.jsx"



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