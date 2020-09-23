export function storeAccessToken(token: string) {
  window.localStorage.setItem("token", token);
}

export function getAccessToken(): string | undefined {
  const token = window.localStorage.getItem("token");
  if (!token) {
    return undefined;
  }
  return token;
}

export function removeAccessToken() {
  window.localStorage.removeItem("token");
}
