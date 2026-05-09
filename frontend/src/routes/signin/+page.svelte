<script lang="ts">
  import { enhance } from "$app/forms";
  import type { PageProps } from "./$types";

  let { data, form }: PageProps = $props();
</script>

<form action="?/signin" method="post" use:enhance class="flex flex-col items-start gap-2 p-2">
  <div class="flex flex-col gap-1">
    <label for="username_input">Nome de Usuário</label>
    {#if form?.detail}
      <input
        id="username_input"
        type="text"
        name="username"
        class="border border-red-500 px-2 py-1"
        maxlength="255"
        autocomplete="off"
        required
      />
    {/if}
    <input
      id="username_input"
      type="text"
      name="username"
      class="px-2 py-1"
      maxlength="255"
      autocomplete="off"
      required
    />
  </div>
  <div class="flex flex-col gap-1">
    <label for="email_input">Email</label>
    <input
      id="email_input"
      type="email"
      name="email"
      class="px-2 py-1"
      maxlength="255"
      autocomplete="email"
      required
    />
  </div>
  <div class="flex flex-col gap-1">
    <label for="password_input">Senha</label>
    <input
      id="password_input"
      type="password"
      name="password"
      class="px-2 py-1"
      maxlength="255"
      minlength="8"
      autocomplete="off"
      required
    />
  </div>
  <div class="flex flex-col gap-1">
    <label for="confirm_password_input">Confirme a Senha</label>
    <input
      id="confirm_password_input"
      type="password"
      name="confirm_password"
      class="px-2 py-1"
      maxlength="255"
      minlength="8"
      autocomplete="off"
      required
    />
    <div id="confirm_password_feedback" class="hidden"></div>
  </div>
  <button
    type="submit"
    class="rounded-md bg-lime-500 px-4 py-2 text-slate-900 shadow-sm hover:cursor-pointer hover:bg-lime-600"
  >
    Cadastrar
  </button>
</form>
