import axios from "axios";
import { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { Link } from "react-router-dom";

function MyQuizzes() {
	const [quizzes, setQuizzes] = useState([]);

	useEffect(() => {
		axios
			.get("http://localhost:8000/quizz_list/")
			.then((response) => {
				console.log(response.data);
				setQuizzes(response.data);
			})
			.catch((error) => {
				console.error("Error fetching quizzes:", error);
			});
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
				{quizzes.map((quiz) => (
					<tr key={quiz.id}>
						<td>{quiz.id}</td>
						<td>
							<Link to={`/quizz_detail/${quiz.id}`}>{quiz.title}</Link>
						</td>
						<td>{quiz.description}</td>
					</tr>
				))}
			</tbody>
		</Table>
	);
}

export default MyQuizzes;
