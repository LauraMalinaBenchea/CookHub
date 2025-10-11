import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

// Attach access token
api.interceptors.request.use((config) => {
	const token = localStorage.getItem("access");
	if (token) config.headers.Authorization = `Bearer ${token}`;
	return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
	(response) => response,
	async (error) => {
		const originalRequest = error.config;
		if (
			error.response?.status === 401 &&
			!originalRequest._retry &&
			localStorage.getItem("refresh")
		) {
			originalRequest._retry = true;
			try {
				const res = await axios.post(
					"http://localhost:8000/api/token/refresh/",
					{
						refresh: localStorage.getItem("refresh"),
					},
				);
				localStorage.setItem("access", res.data.access);
				originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
				return api(originalRequest); // Retry the original request
			} catch (err) {
				console.error("Refresh token failed", err);
				localStorage.removeItem("access");
				localStorage.removeItem("refresh");
				window.location.href = "/login"; // redirect to login
			}
		}
		return Promise.reject(error);
	},
);

export default api;
