import { useCallback, useEffect, useState } from "react";
import { Button, Modal } from "react-bootstrap";
import Table from "react-bootstrap/Table";
import { Link } from "react-router-dom";
import api from "../api";
import RecipeFilter from "../components/RecipeFilter";

function MyRecipes() {
	const [recipes, setRecipes] = useState([]);
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const [selectedRecipeId, setSelectedRecipeId] = useState(null);

	const fetchRecipes = useCallback((filters = {}) => {
		const payload = { ...filters, my_recipes: true }; // flatten
		if (payload.ingredients || payload.title || payload.creator) {
			api
				.post("/recommend_recipes_db/", payload)
				.then((res) => setRecipes(res.data))
				.catch((err) => console.error(err));
		} else {
			api
				.get("/recipe_list/")
				.then((res) => setRecipes(res.data))
				.catch((err) => console.error(err));
		}
	}, []);

	const handleSurpriseMe = (filtersWithNum) => {
		const payload = { ...filtersWithNum, my_recipes: true };
		api
			.post("/recommend_recipes_db/", payload)
			.then((res) => setRecipes(res.data))
			.catch((err) => console.error(err));
	};

	useEffect(() => {
		fetchRecipes();
	}, [fetchRecipes]);

	useEffect(() => {
		api
			.get("/recipe_list/")
			.then((response) => {
				setRecipes(response.data);
			})
			.catch((error) => {
				console.error("Error fetching recipes:", error);
			});
	}, []);

	const handleDelete = async () => {
		try {
			await api.delete(`/recipe_detail/${selectedRecipeId}/`);
			// Refresh the recipes list
			setRecipes((prev) => prev.filter((r) => r.id !== selectedRecipeId));
			setShowDeleteModal(false);
		} catch (err) {
			console.error("Failed to delete recipe:", err);
			console.log("Trying to delete recipe with id", selectedRecipeId);
		}
	};

	return (
		<>
			<RecipeFilter
				onFilterChange={fetchRecipes}
				showCreator={false}
				onSurpriseMe={handleSurpriseMe}
			/>
			<Table striped bordered hover>
				<thead>
					<tr>
						<th>#</th>
						<th>Title</th>
						<th>Description</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{recipes.map((recipe, index) => (
						<tr key={recipe.id}>
							<td>{index + 1}</td>
							<td>
								<Link to={`/edit_recipe/${recipe.id}`}>{recipe.title}</Link>
							</td>
							<td>{recipe.description}</td>
							<td>
								<Button
									variant="danger"
									size="sm"
									onClick={() => {
										setSelectedRecipeId(recipe.id);
										setShowDeleteModal(true);
									}}
								>
									Delete
								</Button>
							</td>
						</tr>
					))}
				</tbody>
			</Table>

			<Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
				<Modal.Header closeButton>
					<Modal.Title>Confirm Delete</Modal.Title>
				</Modal.Header>
				<Modal.Body>Are you sure you want to delete this recipe?</Modal.Body>
				<Modal.Footer>
					<Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
						Cancel
					</Button>
					<Button variant="danger" onClick={handleDelete}>
						Delete
					</Button>
				</Modal.Footer>
			</Modal>
		</>
	);
}

export default MyRecipes;
