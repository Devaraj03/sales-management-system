import { createContext, useContext, useState, useCallback } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("salesman_user");
    return raw ? JSON.parse(raw) : null;
  });

  const login = useCallback(async (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);

    const resp = await api.post("/api/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const { access_token, role, full_name, user_id } = resp.data;
    const userInfo = { full_name, role, user_id };
    localStorage.setItem("salesman_token", access_token);
    localStorage.setItem("salesman_user", JSON.stringify(userInfo));
    setUser(userInfo);
    return userInfo;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("salesman_token");
    localStorage.removeItem("salesman_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
