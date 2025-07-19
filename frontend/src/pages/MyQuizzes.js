import axios from "axios";
import { useEffect, useState } from "react";
import { Button, Modal } from "react-bootstrap";
import Table from "react-bootstrap/Table";
import { Link } from "react-router-dom";

function MyQuizzes() {
	const [quizzes, setQuizzes] = useState([]);
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const [selectedQuizId, setSelectedQuizId] = useState(null);

	useEffect(() => {
		axios
			.get("http://localhost:8000/quiz_list/")
			.then((response) => {
				console.log(response.data);
				setQuizzes(response.data);
			})
			.catch((error) => {
				console.error("Error fetching quizzes:", error);
			});
	}, []);

	const handleDelete = async () => {
		try {
			await axios.delete(
				`http://localhost:8000/quiz_detail/${selectedQuizId}/`,
			);
			// Refresh the quiz list:
			setQuizzes((prev) => prev.filter((q) => q.id !== selectedQuizId));
			setShowDeleteModal(false);
		} catch (err) {
			console.error("Failed to delete quiz:", err);
			console.log("Trying to delete quiz with id ", selectedQuizId);
		}
	};

	return (
		<>
			<Table striped bordered hover>
				<thead>
					<tr>
						<th>#</th>
						<th>Title</th>
						<th>Description</th>
					</tr>
				</thead>
				<tbody>
					{quizzes.map((quiz, qIndex) => (
						<tr key={quiz.id}>
							<td>{qIndex + 1}</td>
							<td>
								<Link to={`/edit_quiz/${quiz.id}`}>{quiz.title}</Link>
							</td>
							<td>{quiz.description}</td>
							<td>
								<Button
									variant="danger"
									size="sm"
									onClick={() => {
										setSelectedQuizId(quiz.id); // store ID
										setShowDeleteModal(true); // show modal
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
				<Modal.Body>Are you sure you want to delete this quiz?</Modal.Body>
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

export default MyQuizzes;
