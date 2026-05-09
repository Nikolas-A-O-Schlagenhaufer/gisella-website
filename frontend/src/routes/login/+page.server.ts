import type { BaseErrorReponseData, Error401ResponseData, TokenReponse } from "$lib/reponse_types";
import { fail, redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";

const LOGIN_URL = "http://localhost:8000/api/user/token";

export const actions = {
  login: async ({ request, cookies }) => {
    const formData = await request.formData();
    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        body: formData
      });
      if (response.status === 401) {
        const error: Error401ResponseData = await response.json();
        return fail(response.status, { detail: error.detail || "Erro durante autenticação." });
      }
      if (!response.ok) {
        const error: BaseErrorReponseData = await response.json();
        return fail(response.status, {
          detail: error.detail || "Erro durante o processo de login. Favor tentar novamente."
        });
      }
      const data: TokenReponse = await response.json();
      const token = data.access_token;
      if (token) {
        cookies.set("access_token", token, {
          path: "/",
          maxAge: data.max_age,
          secure: true,
          httpOnly: true,
          sameSite: "lax"
        });
      }
    } catch (error) {
      return fail(500, { detail: "Erro de conexão com a API." });
    }
    redirect(303, "/");
  }
} satisfies Actions;
