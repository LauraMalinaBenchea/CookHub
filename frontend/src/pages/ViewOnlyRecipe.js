import { useCallback, useEffect, useState } from "react";
import { Alert, Button, Container, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import api from "../api";

function ViewRecipe() {
	const { id } = useParams();
	const [recipe, setRecipe] = useState(null);
	const [error, setError] = useState("");
	const [system, setSystem] = useState("metric");

	const fetchRecipe = useCallback(
		async (systemParam = system) => {
			try {
				const res = await api.get(
					`/recipe_detail/${id}/?system=${systemParam}`,
				);
				setRecipe(res.data);
			} catch (err) {
				console.error(err);
				setError("Could not load recipe.");
			}
		},
		[id, system], // stable dependencies
	);

	useEffect(() => {
		fetchRecipe();
	}, [fetchRecipe]);

	const switchSystem = () => {
		const newSystem = system === "metric" ? "imperial" : "metric";
		setSystem(newSystem);
		fetchRecipe(newSystem);
	};

	if (error) return <Alert variant="danger">{error}</Alert>;
	if (!recipe) return <Spinner animation="border" />;

	return (
		<Container className="mt-4">
			<h2>{recipe.title}</h2>
			<p>
				<strong>Servings:</strong> {recipe.servings}
			</p>

			<h4 className="mt-4 mb-2">Ingredients</h4>
			<div className="text-end mb-3">
				<Button variant="outline-secondary" size="sm" onClick={switchSystem}>
					Switch to {system === "metric" ? "Imperial" : "Metric"}
				</Button>
			</div>

			<ul>
				{recipe.ingredients.map((ing) => (
					<li key={ing.id}>
						{ing.quantity} {ing.unit} of {ing.ingredient}
					</li>
				))}
			</ul>

			<h4 className="mt-4">Preparation</h4>
			<ol>
				{recipe.steps
					.sort((a, b) => a.order - b.order)
					.map((s) => (
						<li key={s.id}>{s.text}</li>
					))}
			</ol>
		</Container>
	);
}

export default ViewRecipe;
