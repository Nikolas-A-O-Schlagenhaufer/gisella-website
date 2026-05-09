const login_form = document.querySelector<HTMLFormElement>("#login_form");

login_form?.addEventListener("submit", (e) => handle_login_form_submit(e));

async function handle_login_form_submit(e: SubmitEvent): Promise<void> {
  e.preventDefault();
  if (!login_form) {
    return;
  }
  const formData = new FormData(login_form);
  try {
    const response = await fetch("/api/user/token", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
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
