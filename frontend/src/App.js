import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "./components/Navbar";
import CreateRecipe from "./pages/CreateRecipe";
import GenerateQuizFromFile from "./pages/GenerateQuizFromFile";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MyRecipes from "./pages/MyRecipes";
import RecipeDetail from "./pages/RecipeDetail";
import Register from "./pages/Register";

function App() {
	return (
		<Router>
			<Navbar />
			<div className="container mt-4">
				<Routes>
					<Route path="/" element={<Home />} />
					<Route path="/login" element={<Login />} />
					<Route path="/register" element={<Register />} />
					<Route path="/create_recipe" element={<CreateRecipe />} />
					<Route path="/edit_recipe/:id" element={<CreateRecipe />} />
					<Route path="/recipe_list" element={<MyRecipes />} />
					<Route path="/recipe_detail/:id" element={<RecipeDetail />} />
					<Route path="/file_upload_quiz/" element={<GenerateQuizFromFile />} />
				</Routes>
			</div>
		</Router>
	);
}

export default App;
