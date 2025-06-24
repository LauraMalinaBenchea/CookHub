import axios from "axios";
import { nanoid } from "nanoid";
import { useState } from "react";
import { Alert, Button, Col, Container, Form, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

function CreateQuizz() {
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
			const response = await axios.post(
				"http://localhost:8000/quizz_list/",
				payload,
			);
			console.log("Quiz created:", response.data);
			navigate("/quizz_list");
		} catch (err) {
			console.error(err);
			setError("Failed to create quiz. Please check all fields and try again.");
		}
	};

	return (
		<Container className="mt-4">
			<h2>Create a New Quiz</h2>
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
								onChange={(e) => handleQuestionChange(qIndex, e)}
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
					Save Quiz
				</Button>
			</Form>
		</Container>
	);
}

export default CreateQuizz;
