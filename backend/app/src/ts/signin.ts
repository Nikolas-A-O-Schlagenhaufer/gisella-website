const password_input =
  document.querySelector<HTMLInputElement>("#password_input");
const confirm_password_input = document.querySelector<HTMLInputElement>(
  "#confirm_password_input",
);
const confirm_password_feedback = document.querySelector<HTMLDivElement>(
  "#confirm_password_feedback",
);
const signin_form = document.querySelector<HTMLFormElement>("#signin_form");

confirm_password_input?.addEventListener(
  "input",
  handle_confirm_password_input_input,
);
signin_form?.addEventListener("submit", (e) => handle_signin_form_submit(e));

function handle_confirm_password_input_input(): boolean | null {
  if (
    !password_input ||
    !confirm_password_input ||
    !confirm_password_feedback
  ) {
    return null;
  }
  const psswd = password_input.value;
  const cnfrm_psswd = confirm_password_input.value;
  if (psswd !== cnfrm_psswd) {
    const message = "As senhas devem ser iguais.";
    confirm_password_feedback.innerText = message;
    confirm_password_feedback.classList.remove("hidden");
    confirm_password_input.setCustomValidity(message);
    return false;
  } else {
    confirm_password_feedback.innerText = "";
    confirm_password_feedback.classList.add("hidden");
    confirm_password_input.setCustomValidity("");
    return true;
  }
}

async function handle_signin_form_submit(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  const match = handle_confirm_password_input_input();
  if (!match || !signin_form) {
    return;
  }
  const formData = new FormData(signin_form);
  const userData = {
    username: formData.get("username")?.toString(),
    email: formData.get("email")?.toString(),
    password: formData.get("password")?.toString(),
  };
  try {
    const response = await fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });
    if (response.ok) {
      window.location.href = "/login";
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
