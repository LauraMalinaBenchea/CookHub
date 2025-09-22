import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

function QuizDetail() {
	const { id } = useParams(); // get the quiz id from the URL
	const [quiz, setQuiz] = useState(null);
	const [error, setError] = useState("");

	useEffect(() => {
		api
			.get(`/quiz_detail/${id}/`)
			.then((res) => {
				setQuiz(res.data);
			})
			.catch((err) => {
				setError("Failed to fetch quiz.");
				console.error(err);
			});
	}, [id]);

	if (error) return <p>{error}</p>;
	if (!quiz) return <p>Loading...</p>;

	return (
		<div>
			<h2>{quiz.title}</h2>
			<p>{quiz.description}</p>

			<h4>Questions</h4>
			{quiz.questions.map((q, qIndex) => (
				<div key={q.id}>
					<strong>{q.question_text}</strong>
					<ul>
						{q.answers.map((a, aIndex) => (
							<li key={a.id}>
								{a.answer_text} {a.correct ? "(Correct)" : ""}
							</li>
						))}
					</ul>
				</div>
			))}
		</div>
	);
}

export default QuizDetail;
