interface UserPrivate {
  id: number;
  username: string;
  email: string;
  image_file?: string;
  image_path: string;
}

let current_user: UserPrivate | null = null;
let fetch_promise: Promise<UserPrivate | null> | null = null;

export async function get_current_user(redirectToLogoutOn401: boolean = true) {
  if (current_user) {
    return current_user;
  }
  if (fetch_promise) {
    return fetch_promise;
  }
  fetch_promise = (async () => {
    try {
      const response = await fetch("/api/user/me", {
        headers: {
          Accept: "application/json",
        },
        credentials: "include",
      });
      if (!response.ok) {
        if (response.status === 401) {
          if (redirectToLogoutOn401) {
            window.location.href = "/api/user/logout";
          }
          return null;
        }
        const error_text = await response.text();
        console.error(
          `Erro ${response.status} durante a busca do usuário atual:`,
          error_text,
        );
        return null;
      }
      current_user = await response.json();
      return current_user;
    } catch (error) {
      console.error("Erro durante a busca do usuário atual:", error);
      return null;
    } finally {
      fetch_promise = null;
    }
  })();
  return fetch_promise;
}

export function clear_user_cache() {
  current_user = null;
}
