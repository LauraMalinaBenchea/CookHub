import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import MyQuizzes from "./pages/MyQuizzes";

function App() {
	return (
		<Router>
			<Navbar />
			<div className="container mt-4">
				<Routes>
					<Route path="/" element={<Home />} />
					<Route path="/quizz_list" element={<MyQuizzes />} />
				</Routes>
			</div>
		</Router>
	);
}

export default App;
