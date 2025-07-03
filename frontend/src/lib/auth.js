// Authentication utilities

export const getToken = () => {
  return localStorage.getItem('auth_token');
};

export const setToken = (token) => {
  localStorage.setItem('auth_token', token);
};

export const removeToken = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
};

export const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

export const isAuthenticated = () => {
  const token = getToken();
  const user = getUser();
  return !!(token && user);
};

export const logout = () => {
  removeToken();
  window.location.href = '/login';
};

