import { useEffect, useState } from "react";
import { Alert, Button, Container, Form } from "react-bootstrap";
import api from "../api";

function ProfilePreferences() {
	const [preferredSystem, setPreferredSystem] = useState("metric");
	const [success, setSuccess] = useState("");
	const [error, setError] = useState("");

	useEffect(() => {
		api
			.get("/user_profile/")
			.then((res) => setPreferredSystem(res.data.preferred_system))
			.catch(() => setError("Failed to load preferences."));
	}, []);

	const handleSave = async (e) => {
		e.preventDefault();
		try {
			await api.put("/user_profile/", { preferred_system: preferredSystem });
			setSuccess("Preferences updated successfully!");
			setError("");
		} catch {
			setError("Could not update preferences.");
			setSuccess("");
		}
	};

	return (
		<Container className="mt-4">
			<h2>Profile Preferences</h2>
			{success && <Alert variant="success">{success}</Alert>}
			{error && <Alert variant="danger">{error}</Alert>}
			<Form onSubmit={handleSave}>
				<Form.Group className="mb-3">
					<Form.Label>Preferred Measuring System</Form.Label>
					<Form.Select
						value={preferredSystem}
						onChange={(e) => setPreferredSystem(e.target.value)}
					>
						<option value="metric">Metric (grams, liters, etc.)</option>
						<option value="imperial">Imperial (ounces, cups, etc.)</option>
					</Form.Select>
				</Form.Group>
				<Button type="submit" variant="primary">
					Save Preferences
				</Button>
			</Form>
		</Container>
	);
}

export default ProfilePreferences;
