import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const Register = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const [success, setSuccess] = useState("");
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError("");
		setSuccess("");

		try {
			await api.post("/register/", { username, password });
			setSuccess("Successfully registered! Redirecting to login...");

			// wait 1.5s then go to login
			setTimeout(() => navigate("/login"), 1500);
		} catch (err) {
			console.error("Registration failed:", err);
			setError("Failed to register. Try again.");
		}
	};

	return (
		<div className="container mt-4">
			<h2>Register</h2>
			{error && <p className="text-danger">{error}</p>}
			{success && <p className="text-success">{success}</p>}
			<form onSubmit={handleSubmit}>
				<div className="mb-3">
					<label htmlFor="username">Username</label>
					<input
						id="username"
						type="text"
						className="form-control"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						required
					/>
				</div>

				<div className="mb-3">
					<label htmlFor="password">Password</label>
					<input
						id="password"
						type="password"
						className="form-control"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
				</div>

				<button type="submit" className="btn btn-primary">
					Register
				</button>
			</form>
		</div>
	);
};

export default Register;
