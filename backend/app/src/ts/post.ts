import { get_current_user } from "./auth.js";

const delete_post_button = document.querySelector<HTMLButtonElement>(
  "#delete_post_button",
);
const delete_post_modal =
  document.querySelector<HTMLDialogElement>("#delete_post_modal");
const delete_post_confirm_button = document.querySelector<HTMLButtonElement>(
  "#delete_post_confirm_button",
);
const post_article_element = document.querySelector<HTMLElement>("article");
const action_buttons_container = document.querySelector<HTMLDivElement>(
  "#action_buttons_container",
);

const post_id = post_article_element?.getAttribute("data-post-id");
const post_user_id = post_article_element?.getAttribute("data-post-user-id");

check_logged_in_user();

delete_post_button?.addEventListener("click", handle_delete_post_button_click);
delete_post_confirm_button?.addEventListener(
  "click",
  handle_delete_post_confirm_button_click,
);

function handle_delete_post_button_click() {
  delete_post_modal?.showModal();
}

async function handle_delete_post_confirm_button_click() {
  if (post_id == null) {
    return console.error("Id da postagem não encontrado.");
  }
  try {
    const response = await fetch(`/api/post/${post_id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (response.status === 401) {
      window.location.href = "/logout";
      return;
    }
    if (response.status === 403) {
      window.alert(
        "Você não está aurotizado a atualizar as informações dessa postagem.",
      );
      return;
    }
    if (response.status === 204) {
      window.location.href = "/";
      return;
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

async function check_logged_in_user(): Promise<void> {
  if (!action_buttons_container || !post_user_id) {
    return;
  }
  const user = await get_current_user();
  if (user && user.id === Number(post_user_id)) {
    action_buttons_container.classList.remove("hidden");
    action_buttons_container.classList.add("flex");
  } else {
    action_buttons_container.classList.add("hidden");
    action_buttons_container.classList.remove("flex");
  }
}
