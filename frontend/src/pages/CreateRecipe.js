import { nanoid } from "nanoid";
import { useEffect, useState } from "react";
import {
	Alert,
	Button,
	Col,
	Container,
	Form,
	Modal,
	Row,
} from "react-bootstrap";
import { useNavigate, useParams } from "react-router-dom";
import AsyncCreatableSelect from "react-select/async-creatable";
import api from "../api";

function CreateRecipe() {
	const { id } = useParams();
	const isEditMode = Boolean(id);

	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [privacy, setPrivacy] = useState("");
	const [servings, setServings] = useState(1);
	const [ingredients, setIngredients] = useState([
		{ id: nanoid(), name: "", quantity: "", unit: "" },
	]);
	const [steps, setSteps] = useState([{ id: nanoid(), text: "" }]);
	const [error, setError] = useState("");
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const [unitOptions, setUnitOptions] = useState([]);
	const [preferredSystem, setPreferredSystem] = useState("metric");

	const navigate = useNavigate();

	// Fetch recipe for edit mode
	useEffect(() => {
		if (!isEditMode) return;
		api
			.get(`/recipe_detail/${id}/`)
			.then((res) => {
				const recipe = res.data;
				setTitle(recipe.title);
				setDescription(recipe.description);
				setPrivacy(recipe.privacy);
				setServings(recipe.servings);
				setIngredients(
					recipe.ingredients.map((ing) => ({
						id: ing.id || nanoid(),
						name: ing.name,
						quantity: ing.quantity,
						unit: ing.unit,
					})),
				);
				setSteps(
					recipe.steps.map((s) => ({ id: s.id || nanoid(), text: s.text })),
				);
			})
			.catch((err) => {
				console.error("Failed to load recipe:", err);
				setError("Could not load recipe for editing.");
			});
	}, [id, isEditMode]);

	useEffect(() => {
		api
			.get("/user_profile/")
			.then((res) => {
				setPreferredSystem(res.data.preferred_system);
				return api.get(`/units/?system=${res.data.preferred_system}`);
			})
			.then((res) => setUnitOptions(res.data))
			.catch(() => setUnitOptions([]));
	}, []);

	// Ingredient handlers
	const handleIngredientChange = (index, field, value) => {
		const updated = [...ingredients];
		updated[index][field] = value;
		setIngredients(updated);
	};

	const addIngredient = () =>
		setIngredients([
			...ingredients,
			{ id: nanoid(), name: "", quantity: "", unit: "" },
		]);
	const removeIngredient = (index) =>
		setIngredients(ingredients.filter((_, i) => i !== index));

	// Step handlers
	const handleStepChange = (index, value) => {
		const updated = [...steps];
		updated[index].text = value;
		setSteps(updated);
	};

	const addStep = () => setSteps([...steps, { id: nanoid(), text: "" }]);
	const removeStep = (index) => setSteps(steps.filter((_, i) => i !== index));

	// Submit
	const handleSubmit = async (e) => {
		e.preventDefault();
		const payload = {
			title,
			description,
			privacy,
			servings,
			ingredients: ingredients.map(({ name, quantity, unit }) => ({
				ingredient: name,
				quantity,
				unit,
			})),
			steps: steps.map(({ text }, index) => ({ text, order: index + 1 })),
		};
		try {
			if (isEditMode) await api.put(`/recipe_detail/${id}/`, payload);
			else await api.post("/recipe_list/", payload);
			navigate("/recipe_list");
		} catch (err) {
			console.error("Failed to save recipe:", err);
			setError("Failed to save recipe. Please check all fields and try again.");
		}
	};

	// Delete
	const handleDelete = async () => {
		try {
			await api.delete(`/recipe_detail/${id}/`);
			navigate("/recipe_list");
		} catch (err) {
			console.error("Delete failed:", err);
			setError("Could not delete recipe.");
		}
	};

	return (
		<Container className="mt-4">
			<h2>{isEditMode ? "Edit Recipe" : "Create a New Recipe"}</h2>
			{error && <Alert variant="danger">{error}</Alert>}
			<Form onSubmit={handleSubmit}>
				<Form.Group className="mb-3">
					<Form.Label>Recipe Title</Form.Label>
					<Form.Control
						type="text"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
						required
					/>
				</Form.Group>
				<Form.Group className="mb-3">
					<Form.Label>Description</Form.Label>
					<Form.Control
						as="textarea"
						rows={3}
						value={description}
						onChange={(e) => setDescription(e.target.value)}
						required
					/>
				</Form.Group>
				<Form.Group className="mb-3">
					<Form.Label>Privacy</Form.Label>
					<Form.Select
						value={privacy}
						onChange={(e) => setPrivacy(e.target.value)}
						required
					>
						<option value="">Select privacy</option>
						<option value="private">Only I can see this</option>
						<option value="public">Anyone can see this</option>
					</Form.Select>
				</Form.Group>
				<hr />
				<Form.Group className="mb-3">
					<Form.Label>Servings</Form.Label>
					<Form.Control
						type="number"
						min={1}
						value={servings}
						onChange={(e) => setServings(Number(e.target.value))}
						required
					/>
				</Form.Group>
				<hr />
				<div className="d-flex justify-content-between align-items-center mb-3">
					<h4>Ingredients</h4>
					<Button
						variant="outline-secondary"
						size="sm"
						onClick={() => {
							const newSystem =
								preferredSystem === "metric" ? "imperial" : "metric";
							setPreferredSystem(newSystem);
							api
								.get(`/units/?system=${newSystem}`)
								.then((res) => setUnitOptions(res.data));
						}}
					>
						Switch to {preferredSystem === "metric" ? "Imperial" : "Metric"}
					</Button>
				</div>
				{ingredients.map((ing, i) => (
					<Row key={ing.id} className="align-items-center mb-2">
						<Col>
							{/* Autocomplete field that allows creating new ingredients, to be handled in serializer*/}
							<AsyncCreatableSelect
								cacheOptions
								defaultOptions
								loadOptions={async (inputValue) => {
									const res = await api.get(
										`/ingredients-autocomplete/?q=${inputValue}`,
									);
									return res.data.map((ing) => ({
										label: ing.name,
										value: ing.name,
									}));
								}}
								value={ing.name ? { label: ing.name, value: ing.name } : null}
								onChange={(selected) =>
									handleIngredientChange(
										i,
										"name",
										selected ? selected.value : "",
									)
								}
							/>
						</Col>
						<Col xs={3}>
							<Form.Control
								type="text"
								value={ing.quantity}
								onChange={(e) =>
									handleIngredientChange(i, "quantity", e.target.value)
								}
								placeholder="Quantity"
								required
							/>
						</Col>

						{/* Unit */}
						<Col xs={3}>
							<Form.Select
								value={ing.unit}
								onChange={(e) =>
									handleIngredientChange(i, "unit", e.target.value)
								}
							>
								<option value="">Select unit</option>
								{unitOptions.map((u) => (
									<option key={u.abbreviation} value={u.abbreviation}>
										{u.name} ({u.abbreviation})
									</option>
								))}
							</Form.Select>
						</Col>
						<Col xs="auto">
							<Button
								variant="danger"
								size="sm"
								onClick={() => removeIngredient(i)}
							>
								×
							</Button>
						</Col>
					</Row>
				))}
				<Button
					variant="secondary"
					size="sm"
					onClick={addIngredient}
					className="mb-3"
				>
					Add Ingredient
				</Button>
				<hr />
				<h4>Steps</h4>
				{steps.map((s, i) => (
					<Row key={s.id} className="align-items-center mb-2">
						<Col>
							<Form.Control
								as="textarea"
								rows={2}
								value={s.text}
								onChange={(e) => handleStepChange(i, e.target.value)}
								placeholder={`Step ${i + 1}`}
								required
							/>
						</Col>
						<Col xs="auto">
							<Button variant="danger" size="sm" onClick={() => removeStep(i)}>
								×
							</Button>
						</Col>
					</Row>
				))}
				<Button
					variant="secondary"
					size="sm"
					onClick={addStep}
					className="mb-3"
				>
					Add Step
				</Button>
				<Button variant="primary" type="submit">
					{isEditMode ? "Update Recipe" : "Save Recipe"}
				</Button>{" "}
				{isEditMode && (
					<>
						<Button variant="danger" onClick={() => setShowDeleteModal(true)}>
							Delete Recipe
						</Button>

						<Modal
							show={showDeleteModal}
							onHide={() => setShowDeleteModal(false)}
						>
							<Modal.Header closeButton>
								<Modal.Title>Confirm Delete</Modal.Title>
							</Modal.Header>
							<Modal.Body>
								Are you sure you want to delete this recipe?
							</Modal.Body>
							<Modal.Footer>
								<Button
									variant="secondary"
									onClick={() => setShowDeleteModal(false)}
								>
									Cancel
								</Button>
								<Button variant="danger" onClick={handleDelete}>
									Delete
								</Button>
							</Modal.Footer>
						</Modal>
					</>
				)}
			</Form>
		</Container>
	);
}

export default CreateRecipe;
