import type { BaseErrorReponseData, Error401ResponseData, TokenReponse } from "$lib/reponse_types";
import { fail, redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";
import type { UserCreate } from "$lib/post_types";

const LOGIN_URL = "http://localhost:8000/api/user";

export const actions = {
  signin: async ({ request }) => {
    const formData = await request.formData();
    const username = formData.get("username")?.toString();
    if (!username) {
      return fail(400, {
        detail: "Nome de usuário não foi informado.",
        field: "username"
      });
    }
    const email = formData.get("email")?.toString();
    if (!email) {
      return fail(400, {
        detail: "Email não foi informado.",
        field: "email"
      });
    }
    const password = formData.get("password")?.toString();
    if (!password) {
      return fail(400, {
        detail: "Senha não foi informada.",
        field: "password"
      });
    }
    const confirm_password = formData.get("confirm_password")?.toString();
    if (password !== confirm_password) {
      return fail(400, {
        detail: "Senhas não são iguais.",
        field: "confirm_password"
      });
    }
    const userData: UserCreate = {
      username,
      email,
      password
    };
    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
      });
      if (response.status === 400) {
        const error: BaseErrorReponseData = await response.json();
        return fail(response.status, {
          detail: error.detail || "Erro durante o cadastro do usuário."
        });
      }
      if (!response.ok) {
        const error: BaseErrorReponseData = await response.json();
        return fail(response.status, {
          detail: error.detail || "Erro durante o cadastro do usuário. Favor tentar novamente."
        });
      }
    } catch (error) {
      return fail(500, { detail: "Erro de conexão com a API." });
    }
    redirect(303, "/login");
  }
} satisfies Actions;
