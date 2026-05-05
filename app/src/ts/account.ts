import { clear_user_cache, get_current_user } from "./auth.js";

const username = document.querySelector<HTMLHeadingElement>("#username");
const email = document.querySelector<HTMLParagraphElement>("#email");
const username_input =
  document.querySelector<HTMLInputElement>("#username_input");
const email_input = document.querySelector<HTMLInputElement>("#email_input");
const update_user_form =
  document.querySelector<HTMLFormElement>("#update_user_form");

update_user_form?.addEventListener("submit", (e) =>
  handle_update_user_form_submit(e),
);

let current_user_id: Number | null = null;

load_user_data();

async function load_user_data(): Promise<void> {
  if (!username || !email) {
    return;
  }
  if (!username_input || !email_input) {
    return;
  }
  const user = await get_current_user(true);
  if (!user) {
    window.location.href = "/login";
    return;
  }
  current_user_id = user.id;
  username.innerText = user.username;
  email.innerText = user.email;
  username_input.value = user.username;
  email_input.value = user.email;
}

async function handle_update_user_form_submit(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  if (!update_user_form || !current_user_id) {
    return;
  }
  if (!username || !email) {
    return;
  }
  const formData = new FormData(update_user_form);
  const userData = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(`/api/user/${current_user_id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      credentials: "include",
      body: JSON.stringify(userData),
    });
    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }
    if (response.status === 403) {
      window.alert(
        "Você não está autorizado a atualizar os dados desse usuário.",
      );
      return;
    }
    if (response.ok) {
      const data = await response.json();
      clear_user_cache();
      username.innerText = data.username;
      email.innerText = data.email;
    } else {
      const error = await response.json();
      window.alert(error);
      return;
    }
  } catch (error) {
    window.alert(error);
    return;
  }
}
