import { useCallback, useEffect, useState } from "react";
import { Alert, Button, Container, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import api from "../api";

function ViewRecipe() {
	const { id } = useParams();
	const [recipe, setRecipe] = useState(null);
	const [error, setError] = useState("");
	const [system, setSystem] = useState("metric");

	// Ratings
	const [userRating, setUserRating] = useState(null); // current user's rating
	const [avgRating, setAvgRating] = useState(null); // average rating

	// Fetch recipe
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
		[id, system],
	);

	useEffect(() => {
		fetchRecipe();
	}, [fetchRecipe]);

	// Fetch ratings after recipe is loaded
	const fetchRatings = useCallback(() => {
		if (!recipe || recipe.created_by === "me") return;

		// Fetch current user's rating
		api
			.get(`/recipe_rating_detail/${id}/`)
			.then((res) => setUserRating(res.data.rating))
			.catch((err) => console.error(err));

		// Fetch average rating
		api
			.get(`/recipe_rating_avg/${id}/`)
			.then((res) => setAvgRating(res.data.avg_rating))
			.catch((err) => console.error(err));
	}, [recipe, id]);

	useEffect(() => {
		fetchRatings();
	}, [fetchRatings]);

	const switchSystem = () => {
		const newSystem = system === "metric" ? "imperial" : "metric";
		setSystem(newSystem);
		fetchRecipe(newSystem);
	};

	const handleRate = (rating) => {
		api
			.post(`/recipe_rating/${id}/`, { rating })
			.then((res) => setUserRating(res.data.rating))
			.catch((err) => console.error(err))
			.finally(() => {
				// Refresh average rating after submission
				api
					.get(`/recipe_rating_avg/${id}/`)
					.then((res) => setAvgRating(res.data.avg_rating))
					.catch((err) => console.error(err));
			});
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

			{/* Ratings */}
			{recipe.created_by !== "me" && (
				<div className="mt-4">
					<h5>Rate this recipe</h5>
					<div className="d-flex align-items-center gap-2">
						{[1, 2, 3, 4, 5].map((star) => (
							<Button
								key={star}
								variant={userRating >= star ? "warning" : "outline-secondary"}
								size="sm"
								onClick={() => handleRate(star)}
							>
								{star}★
							</Button>
						))}
						{avgRating !== null && (
							<span className="ms-3">Average: {avgRating.toFixed(2)}★</span>
						)}
					</div>
				</div>
			)}
		</Container>
	);
}

export default ViewRecipe;
