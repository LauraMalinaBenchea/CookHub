import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { AuthContext } from "../context/AuthContext";

function Login() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const navigate = useNavigate();
	const { isLoggedIn, login } = useContext(AuthContext);

	// ✅ Redirect if already logged in
	useEffect(() => {
		if (isLoggedIn) {
			navigate("/public_recipe_list", { replace: true });
		}
	}, [isLoggedIn, navigate]);

	const [error, setError] = useState("");

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			const response = await api.post("/api/token/", { username, password });

			login(response.data.access, response.data.refresh);

			navigate("/public_recipe_list");
		} catch (err) {
			console.error("Login failed:", err);
			setError("Invalid username or password");
		}
	};

	return (
		<div className="container mt-4">
			<h2>Login</h2>
			{error && <div className="alert alert-danger">{error}</div>}
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
					Log in
				</button>
			</form>
		</div>
	);
}

export default Login;
