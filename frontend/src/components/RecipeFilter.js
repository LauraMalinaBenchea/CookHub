import { useState } from "react";
import { Button, Col, Form, InputGroup, Row } from "react-bootstrap";
import AsyncCreatableSelect from "react-select/async-creatable";
import api from "../api";

function RecipeFilter({ onFilterChange, onSurpriseMe, showCreator = true }) {
	const [ingredients, setIngredients] = useState([]);
	const [title, setTitle] = useState("");
	const [creator, setCreator] = useState("");
	const [numRandom, setNumRandom] = useState(1);

	const handleSubmit = (e) => {
		e.preventDefault();
		const ingredientNames = ingredients.map((i) => i.value);
		onFilterChange({
			title,
			creator: showCreator ? creator : undefined,
			ingredients: ingredientNames,
		});
	};

	const handleReset = () => {
		setTitle("");
		setCreator("");
		setIngredients([]);
		setNumRandom(1);
		onFilterChange({});
	};

	const handleSurpriseMe = () => {
		const ingredientNames = ingredients.map((i) => i.value);
		onSurpriseMe({
			title,
			creator: showCreator ? creator : undefined,
			ingredients: ingredientNames,
			num_choices: Number(numRandom) || 1,
		});
	};

	return (
		<Form onSubmit={handleSubmit} className="mb-3">
			<Row className="align-items-end">
				<Col>
					<Form.Label>Title</Form.Label>
					<Form.Control
						type="text"
						placeholder="Recipe title or keyword"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
					/>
				</Col>

				{showCreator && (
					<Col>
						<Form.Label>Creator</Form.Label>
						<Form.Control
							type="text"
							placeholder="User who created it"
							value={creator}
							onChange={(e) => setCreator(e.target.value)}
						/>
					</Col>
				)}

				<Col>
					<Form.Label>Ingredients</Form.Label>
					<AsyncCreatableSelect
						isMulti
						cacheOptions
						defaultOptions
						loadOptions={async (inputValue) => {
							const res = await api.get(
								`/ingredients-autocomplete/?q=${inputValue}`,
							);
							return res.data.map((i) => ({ label: i.name, value: i.name }));
						}}
						value={ingredients}
						onChange={setIngredients}
					/>
				</Col>

				<Col xs="auto" className="d-flex gap-2">
					<Button type="submit">Filter</Button>
					<Button variant="secondary" onClick={handleReset}>
						Reset Filters
					</Button>
				</Col>
			</Row>

			<Row className="align-items-center mt-2">
				<Col xs="auto">
					<InputGroup>
						<InputGroup.Text>Surprise me:</InputGroup.Text>
						<Form.Control
							type="number"
							min={1}
							value={numRandom}
							onChange={(e) => setNumRandom(e.target.value)}
						/>
						<Button variant="warning" onClick={handleSurpriseMe}>
							Go!
						</Button>
					</InputGroup>
				</Col>
			</Row>
		</Form>
	);
}

export default RecipeFilter;
