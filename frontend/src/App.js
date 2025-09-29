import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "./components/Navbar";
import CreateQuiz from "./pages/CreateQuiz";
import GenerateQuizFromFile from "./pages/GenerateQuizFromFile";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MyQuizzes from "./pages/MyQuizzes";
import QuizDetail from "./pages/QuizDetail";
import Register from "./pages/Register";

function App() {
	return (
		<Router>
			<Navbar />
			<div className="container mt-4">
				<Routes>
					<Route path="/" element={<Home />} />
					<Route path="/login" element={<Login />} />
					<Route path="/register" element={<Register />} /> {/* ✅ add this */}
					<Route path="/create_quiz" element={<CreateQuiz />} />
					<Route path="/edit_quiz/:id" element={<CreateQuiz />} />
					<Route path="/quiz_list" element={<MyQuizzes />} />
					<Route path="/quiz_detail/:id" element={<QuizDetail />} />
					<Route path="/file_upload_quiz/" element={<GenerateQuizFromFile />} />
				</Routes>
			</div>
		</Router>
	);
}

export default App;
