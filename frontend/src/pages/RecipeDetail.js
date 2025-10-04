import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

function RecipeDetail() {
	const { id } = useParams(); // get the recipe id from the URL
	const [recipe, setRecipe] = useState(null);
	const [error, setError] = useState("");

	useEffect(() => {
		api
			.get(`/recipe_detail/${id}/`)
			.then((res) => {
				setRecipe(res.data);
			})
			.catch((err) => {
				setError("Failed to fetch recipe.");
				console.error(err);
			});
	}, [id]);

	if (error) return <p>{error}</p>;
	if (!recipe) return <p>Loading...</p>;

	return (
		<div>
			<h2>{recipe.title}</h2>
			<p>{recipe.description}</p>
			<p>Servings: {recipe.servings}</p>

			<h4>Ingredients</h4>
			<ul>
				{recipe.ingredients?.map((ri) => (
					<li key={ri.id}>
						{ri.quantity} {ri.unit} {ri.ingredient.name}
					</li>
				))}
			</ul>

			<h4>Steps</h4>
			<ol>
				{recipe.steps?.map((step) => (
					<li key={step.id}>{step.text}</li>
				))}
			</ol>
		</div>
	);
}

export default RecipeDetail;
