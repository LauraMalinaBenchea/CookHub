import { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { Link } from "react-router-dom";
import api from "../api";

function PublicRecipes() {
	const [recipes, setRecipes] = useState([]);

	useEffect(() => {
		api
			.get("/public_recipe_list/")
			.then((res) => setRecipes(res.data))
			.catch((err) => console.error("Error fetching public recipes:", err));
	}, []);

	return (
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
							<Link to={`/edit_recipe/${recipe.id}`}>{recipe.title}</Link>
						</td>
						<td>{recipe.description}</td>
					</tr>
				))}
			</tbody>
		</Table>
	);
}

export default PublicRecipes;
