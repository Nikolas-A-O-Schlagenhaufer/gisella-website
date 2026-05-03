const new_post_button =
  document.querySelector<HTMLButtonElement>("#new_post_button");
const new_post_modal =
  document.querySelector<HTMLDialogElement>("#new_post_modal");
const new_post_form = document.querySelector<HTMLFormElement>("#new_post_form");
const dark_mode_toggle_button = document.querySelector<HTMLButtonElement>(
  "#dark_mode_toggle_button",
);

const dark_mode_svg = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#f8fafc"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Zm0-80q88 0 158-48.5T740-375q-20 5-40 8t-40 3q-123 0-209.5-86.5T364-660q0-20 3-40t8-40q-78 32-126.5 102T200-480q0 116 82 198t198 82Zm-10-270Z"/></svg>`;
const light_mode_svg = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#0f172b"><path d="M565-395q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35Zm-226.5 56.5Q280-397 280-480t58.5-141.5Q397-680 480-680t141.5 58.5Q680-563 680-480t-58.5 141.5Q563-280 480-280t-141.5-58.5ZM200-440H40v-80h160v80Zm720 0H760v-80h160v80ZM440-760v-160h80v160h-80Zm0 720v-160h80v160h-80ZM256-650l-101-97 57-59 96 100-52 56Zm492 496-97-101 53-55 101 97-57 59Zm-98-550 97-101 59 57-100 96-56-52ZM154-212l101-97 55 53-97 101-59-57Zm326-268Z"/></svg>`;

let dark_mode: boolean = true;
const user_selection = localStorage.getItem("mode");
if (user_selection != null) {
  dark_mode = user_selection === "dark";
}
document.documentElement.classList.toggle("dark", dark_mode);
update_dark_mode_toggle_button_icon();

new_post_button?.addEventListener("click", open_new_post_modal);
new_post_form?.addEventListener("submit", (e) =>
  handle_new_post_form_submit(e),
);
dark_mode_toggle_button?.addEventListener(
  "click",
  handle_dark_mode_toggle_button,
);

function open_new_post_modal(): void {
  new_post_modal?.showModal();
}

async function handle_new_post_form_submit(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  if (!new_post_form) {
    return;
  }
  const formData = new FormData(new_post_form);
  formData.set("user_id", "1");
  const postData = Object.fromEntries(formData.entries());
  try {
    const response = await fetch("/api/post", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postData),
    });
    if (response.ok) {
      new_post_form.reset();
      new_post_modal?.close();
      window.location.reload();
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

function handle_dark_mode_toggle_button(): void {
  dark_mode = !dark_mode;
  localStorage.setItem("mode", dark_mode ? "dark" : "light");
  document.documentElement.classList.toggle("dark", dark_mode);
  update_dark_mode_toggle_button_icon();
}

function update_dark_mode_toggle_button_icon(): void {
  if (dark_mode_toggle_button == null) {
    return;
  }
  if (dark_mode) {
    dark_mode_toggle_button.innerHTML = dark_mode_svg;
  } else {
    dark_mode_toggle_button.innerHTML = light_mode_svg;
  }
}
