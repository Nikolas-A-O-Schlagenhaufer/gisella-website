const delete_post_button = document.querySelector<HTMLButtonElement>(
  "#delete_post_button",
);
const delete_post_modal =
  document.querySelector<HTMLDialogElement>("#delete_post_modal");
const delete_post_confirm_button = document.querySelector<HTMLButtonElement>(
  "#delete_post_confirm_button",
);
const post_article_element = document.querySelector<HTMLElement>("article");

const post_id = post_article_element?.getAttribute("data-post-id");

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
    });
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
