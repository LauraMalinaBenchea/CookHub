import { useCallback, useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { Link } from "react-router-dom";
import api from "../api";
import RecipeFilter from "../components/RecipeFilter";

function PublicRecipes() {
	const [recipes, setRecipes] = useState([]);

	const fetchRecipes = useCallback((filters = {}) => {
		const payload = { ...filters }; // flatten
		if (payload.ingredients || payload.title || payload.creator) {
			api
				.post("/recommend_recipes_db/", payload)
				.then((res) => setRecipes(res.data))
				.catch((err) => console.error(err));
		} else {
			api
				.get("/public_recipe_list/")
				.then((res) => setRecipes(res.data))
				.catch((err) => console.error(err));
		}
	}, []);

	const handleSurpriseMe = (filtersWithNum) => {
		api
			.post("/recommend_recipes_db/", filtersWithNum)
			.then((res) => setRecipes(res.data))
			.catch((err) => console.error(err));
	};

	useEffect(() => {
		fetchRecipes();
	}, [fetchRecipes]);

	return (
		<>
			<RecipeFilter
				onFilterChange={fetchRecipes}
				showCreator={true}
				onSurpriseMe={handleSurpriseMe}
			/>
			<Table striped bordered hover>
				<thead>
					<tr>
						<th>#</th>
						<th>Title</th>
						<th>Description</th>
					</tr>
				</thead>
				<tbody>
					{recipes.map((recipe, index) => (
						<tr key={recipe.id}>
							<td>{index + 1}</td>
							<td>
								<Link to={`/view_only_recipe/${recipe.id}`}>
									{recipe.title}
								</Link>
							</td>
							<td>{recipe.description}</td>
						</tr>
					))}
				</tbody>
			</Table>
		</>
	);
}

export default PublicRecipes;
