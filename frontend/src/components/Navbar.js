import { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "bootstrap/dist/css/bootstrap.min.css";

const Navbar = () => {
	const { isLoggedIn, logout } = useContext(AuthContext);
	const navigate = useNavigate();

	const handleLogout = () => {
		logout();
		navigate("/login");
	};

	return (
		<nav className="navbar navbar-expand-lg navbar-dark bg-dark">
			<div className="container-fluid">
				<Link className="navbar-brand" to="/">
					My Quiz App
				</Link>
				<button
					className="navbar-toggler"
					type="button"
					data-bs-toggle="collapse"
					data-bs-target="#navbarNav"
				>
					<span className="navbar-toggler-icon"></span>
				</button>

				<div className="collapse navbar-collapse" id="navbarNav">
					{/* Left side navigation */}
					<ul className="navbar-nav me-auto">
						<li className="nav-item">
							<Link className="nav-link" to="/create_quiz">
								Generate New Quiz
							</Link>
						</li>
						<li className="nav-item">
							<Link className="nav-link" to="/quiz_list">
								See My Quizzes
							</Link>
						</li>
						<li className="nav-item">
							<Link className="nav-link" to="/file_upload_quiz">
								Generate Quiz From File
							</Link>
						</li>
					</ul>

					<ul className="navbar-nav ms-auto">
						{!isLoggedIn
							? <>
									<li className="nav-item">
										<Link className="nav-link" to="/login">
											Login
										</Link>
									</li>
									<li className="nav-item">
										<Link className="nav-link" to="/register">
											Register
										</Link>
									</li>
								</>
							: <li className="nav-item">
									<button
										type="button"
										className="btn btn-outline-danger btn-sm ms-2"
										onClick={handleLogout}
									>
										Logout
									</button>
								</li>}
					</ul>
				</div>
			</div>
		</nav>
	);
};

export default Navbar;
