<script lang="ts">
  import "./layout.css";
  import favicon from "$lib/assets/favicon.svg";
  import type { LayoutProps } from "./$types";
  import BaseModal from "$lib/components/BaseModal.svelte";

  let { data, children }: LayoutProps = $props();
  let new_post_modal: BaseModal | undefined = $state();
  const new_post_modal_id = "new_post_modal";
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<nav class="flex items-center justify-between p-2">
  <a href="/">Website Gisella</a>
  <div class="flex items-center justify-center gap-1">
    {#if data.user}
      <button
        type="button"
        class="rounded-md bg-cyan-400 px-4 py-2 text-slate-900 shadow-sm hover:cursor-pointer hover:bg-cyan-500"
        onclick={() => new_post_modal?.open()}>Nova Postagem</button
      >
      <span>{data.user.email}</span>
      <form action="/logout" method="post">
        <button type="submit" class="hover:cursor-pointer">Sair</button>
      </form>
    {:else}
      <a href="/signin">Cadastrar</a>
      <a href="/login">Entrar</a>
    {/if}
  </div>
</nav>

{@render children()}

{#if data.user}
  <BaseModal id={new_post_modal_id} title={"Nova Postagem"} bind:this={new_post_modal} />
{/if}
