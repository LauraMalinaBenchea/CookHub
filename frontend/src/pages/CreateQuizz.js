import axios from "axios";
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

function CreateQuizz() {
	const { id } = useParams();
	const isEditMode = Boolean(id);

	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [questions, setQuestions] = useState([
		{
			id: nanoid(),
			question_text: "",
			answers: [{ id: nanoid(), answer_text: "", correct: false }],
		},
	]);
	const [error, setError] = useState("");
	const navigate = useNavigate();

	// Fetch quiz data for edit mode
	useEffect(() => {
		if (isEditMode) {
			axios
				.get(`http://localhost:8000/quizz_detail/${id}/`)
				.then((res) => {
					const quiz = res.data;
					setTitle(quiz.title);
					setDescription(quiz.description);
					setQuestions(
						quiz.questions.map((q) => ({
							id: nanoid(),
							question_text: q.question_text,
							answers: q.answers.map((a) => ({
								id: nanoid(),
								answer_text: a.answer_text,
								correct: a.correct,
							})),
						})),
					);
				})
				.catch((err) => {
					console.error("Failed to load quiz:", err);
					setError("Could not load quiz for editing.");
				});
		}
	}, [isEditMode, id]);

	const handleQuestionChange = (qIndex, e) => {
		const updated = [...questions];
		updated[qIndex].question_text = e.target.value;
		setQuestions(updated);
	};

	const handleAnswerChange = (qIndex, aIndex, field, value) => {
		const updated = [...questions];
		updated[qIndex].answers[aIndex][field] = value;
		setQuestions(updated);
	};

	const addQuestion = () => {
		setQuestions([
			...questions,
			{
				id: nanoid(),
				question_text: "",
				answers: [{ id: nanoid(), answer_text: "", correct: false }],
			},
		]);
	};

	const removeQuestion = (qIndex) => {
		const updated = [...questions];
		updated.splice(qIndex, 1);
		setQuestions(updated);
	};

	const addAnswer = (qIndex) => {
		const updated = [...questions];
		updated[qIndex].answers.push({
			id: nanoid(),
			answer_text: "",
			correct: false,
		});
		setQuestions(updated);
	};

	const removeAnswer = (qIndex, aIndex) => {
		const updated = [...questions];
		updated[qIndex].answers.splice(aIndex, 1);
		setQuestions(updated);
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		const payload = {
			title,
			description,
			questions: questions.map((q) => ({
				question_text: q.question_text,
				answers: q.answers.map((a) => ({
					answer_text: a.answer_text,
					correct: a.correct,
				})),
			})),
		};

		try {
			if (isEditMode) {
				await axios.put(`http://localhost:8000/quizz_detail/${id}/`, payload);
			} else {
				await axios.post(`http://localhost:8000/quizz_list/`, payload);
			}
			navigate("/quizz_list");
		} catch (err) {
			console.error("Failed to save quiz:", err);
			setError("Failed to save quiz. Please check all fields and try again.");
		}
	};
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const handleDelete = async () => {
		try {
			await axios.delete(`http://localhost:8000/quizz_detail/${id}/`);
			navigate("/quizz_list");
		} catch (err) {
			console.error("Delete failed:", err);
			setError("Could not delete quiz.");
		}
	};

	return (
		<Container className="mt-4">
			<h2>{isEditMode ? "Edit Quiz" : "Create a New Quiz"}</h2>
			{error && <Alert variant="danger">{error}</Alert>}
			<Form onSubmit={handleSubmit}>
				<Form.Group className="mb-3">
					<Form.Label>Quiz Title</Form.Label>
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
				<hr />
				<h4>Questions</h4>
				{questions.map((q, qIndex) => (
					<div key={q.id} className="mb-4 p-3 border rounded bg-light">
						<Form.Group className="mb-2">
							<Form.Label>Question {qIndex + 1}</Form.Label>
							<Form.Control
								type="text"
								value={q.question_text}
								onChange={(e) => handleQuestionChange(q.id, e)}
								required
							/>
						</Form.Group>
						<h6>Answers</h6>
						{q.answers.map((a, aIndex) => (
							<Row key={a.id} className="align-items-center mb-2">
								<Col>
									<Form.Control
										type="text"
										value={a.answer_text}
										onChange={(e) =>
											handleAnswerChange(
												qIndex,
												aIndex,
												"answer_text",
												e.target.value,
											)
										}
										placeholder={`Answer ${aIndex + 1}`}
										required
									/>
								</Col>
								<Col xs="auto">
									<Form.Check
										type="checkbox"
										label="Correct"
										checked={a.correct}
										onChange={(e) =>
											handleAnswerChange(
												qIndex,
												aIndex,
												"correct",
												e.target.checked,
											)
										}
									/>
								</Col>
								<Col xs="auto">
									<Button
										variant="danger"
										size="sm"
										onClick={() => removeAnswer(qIndex, aIndex)}
									>
										×
									</Button>
								</Col>
							</Row>
						))}
						<Button
							variant="secondary"
							size="sm"
							onClick={() => addAnswer(qIndex)}
						>
							Add Answer
						</Button>{" "}
						{questions.length > 1 && (
							<Button
								variant="outline-danger"
								size="sm"
								onClick={() => removeQuestion(qIndex)}
							>
								Remove Question
							</Button>
						)}
					</div>
				))}
				<Button variant="info" className="mb-3" onClick={addQuestion}>
					Add Question
				</Button>
				<br />
				<Button variant="primary" type="submit">
					{isEditMode ? "Update Quiz" : "Save Quiz"}
				</Button>{" "}
				{isEditMode && (
					<>
						<Button variant="danger" onClick={() => setShowDeleteModal(true)}>
							Delete Quiz
						</Button>

						<Modal
							show={showDeleteModal}
							onHide={() => setShowDeleteModal(false)}
						>
							<Modal.Header closeButton>
								<Modal.Title>Confirm Delete</Modal.Title>
							</Modal.Header>
							<Modal.Body>
								Are you sure you want to delete this quiz?
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

export default CreateQuizz;
