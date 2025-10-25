import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "./components/Navbar";
import CreateRecipe from "./pages/CreateRecipe";
import GenerateRecipeFromFile from "./pages/GenerateRecipeFromFile";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MyRecipes from "./pages/MyRecipes";
import ProfilePreferences from "./pages/ProfilePreferences";
import PublicRecipes from "./pages/PublicRecipes";
import RecipeDetail from "./pages/RecipeDetail";
import Register from "./pages/Register";
import ViewRecipe from "./pages/ViewOnlyRecipe";

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
					<Route path="/public_recipe_list" element={<PublicRecipes />} />
					<Route path="/recipe_detail/:id" element={<RecipeDetail />} />
					<Route
						path="/file_upload_recipe/"
						element={<GenerateRecipeFromFile />}
					/>
					<Route path="/user_profile/" element={<ProfilePreferences />} />
					<Route path="/view_only_recipe/:id" element={<ViewRecipe />} />
				</Routes>
			</div>
		</Router>
	);
}

export default App;
