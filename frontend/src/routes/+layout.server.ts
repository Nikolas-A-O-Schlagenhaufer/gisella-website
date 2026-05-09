import { error } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";
import type { UserPrivate } from "$lib/model_types";

const GET_CURRENT_USER_URL = "http://localhost:8000/api/user/me";

export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
  const token = cookies.get("access_token");
  if (!token) {
    return { user: null };
  }
  try {
    const response = await fetch(GET_CURRENT_USER_URL, {
      headers: {
        Accept: "application/json",
        Cookie: `access_token=${token}`
      },
      credentials: "include"
    });
    if (!response.ok) {
      return { user: null };
    }
    const user: UserPrivate = await response.json();
    return { user: user };
  } catch (err) {
    error(500, { message: "Ocorreu um error durante a busca do usuário." });
  }
};
