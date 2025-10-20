import { useState } from "react";
import { Alert, Button, Container, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import api from "../api";

function GenerateRecipeFromFile() {
	const [file, setFile] = useState(null);
	const [error, setError] = useState("");
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		if (!file) {
			setError("No file selected.");
			return;
		}
		const formData = new FormData();
		formData.append("name", file.name);
		formData.append("file", file);
		try {
			const response = await api.post("/upload/", formData, {
				headers: { "Content-Type": "multipart/form-data" },
			});
			alert("File uploaded successfully!");

			const recipeId = response.data.recipe.id;
			navigate(`/editRecipe/${recipeId}`);
		} catch (err) {
			console.error("Upload error:", err.response?.data || err.message);
			let errorMsg = "Failed to upload file.";
			if (err.response?.data) {
				errorMsg = Object.entries(err.response.data)
					.map(([field, messages]) => {
						if (Array.isArray(messages)) {
							return `${field}: ${messages.join(", ")}`;
						} else {
							// fallback if it's a string or something else
							return `${field}: ${messages}`;
						}
					})
					.join(" | ");
			}

			setError(errorMsg);
		}
	};
	return (
		<Container className="mt-4">
			<h2> Upload File </h2>
			{error && <Alert variant="danger">{error}</Alert>}
			<Form onSubmit={handleSubmit}>
				<Form.Group className="mb-3">
					<Form.Label htmlFor="fileInput">Select file</Form.Label>
					<Form.Control
						id="fileInput"
						type="file"
						required
						onChange={(e) => setFile(e.target.files[0])}
					/>
				</Form.Group>
				<Button variant="primary" type="submit">
					Generate Recipe from file
				</Button>
			</Form>
		</Container>
	);
}

export default GenerateRecipeFromFile;
