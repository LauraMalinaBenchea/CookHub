import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "./components/Navbar";
import CreateQuizz from "./pages/CreateQuizz";
import Home from "./pages/Home";
import MyQuizzes from "./pages/MyQuizzes";
import QuizzDetail from "./pages/QuizzDetail";

function App() {
	return (
		<Router>
			<Navbar />
			<div className="container mt-4">
				<Routes>
					<Route path="/" element={<Home />} />
					<Route path="/create_quizz" element={<CreateQuizz />} />
					<Route path="/edit_quizz/:id" element={<CreateQuizz />} />
					<Route path="/quizz_list" element={<MyQuizzes />} />
					<Route path="/quizz_detail/:id" element={<QuizzDetail />} />
				</Routes>
			</div>
		</Router>
	);
}

export default App;
