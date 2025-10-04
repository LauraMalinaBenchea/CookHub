import { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
	const [isLoggedIn, setIsLoggedIn] = useState(
		!!localStorage.getItem("access"),
	);

	useEffect(() => {
		const handleStorageChange = () => {
			setIsLoggedIn(!!localStorage.getItem("access"));
		};
		window.addEventListener("storage", handleStorageChange);
		return () => window.removeEventListener("storage", handleStorageChange);
	}, []);

	const login = (access, refresh) => {
		localStorage.setItem("access", access);
		localStorage.setItem("refresh", refresh);
		setIsLoggedIn(true);
	};

	const logout = () => {
		localStorage.removeItem("access");
		localStorage.removeItem("refresh");
		setIsLoggedIn(false);
	};

	return (
		<AuthContext.Provider value={{ isLoggedIn, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
};
