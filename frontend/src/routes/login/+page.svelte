<script lang="ts">
  import { enhance } from "$app/forms";
  import type { PageProps } from "./$types";

  let { data, form }: PageProps = $props();
</script>

<form action="?/login" method="post" use:enhance class="flex flex-col items-start gap-2 p-2">
  <div class="flex flex-col gap-1">
    {#if form?.detail}
      <p>{form.detail}</p>
    {/if}
    <label for="email_input">Email</label>
    <input
      id="email_input"
      type="email"
      name="username"
      class="rounded-md px-2 py-1"
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
      class="rounded-md px-2 py-1"
      maxlength="255"
      minlength="8"
      autocomplete="off"
      required
    />
  </div>
  <button
    type="submit"
    class="rounded-md bg-lime-500 px-4 py-2 text-slate-900 shadow-sm hover:cursor-pointer hover:bg-lime-600"
  >
    Entrar
  </button>
</form>
