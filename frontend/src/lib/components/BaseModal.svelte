<script lang="ts">
  interface Props {
    id: string;
    title: string;
  }
  let { id, title }: Props = $props();
  let dialog: HTMLDialogElement | undefined = $state();

  export function open() {
    if (!dialog) {
      return;
    }
    dialog.showModal();
  }

  export function close() {
    if (!dialog) {
      return;
    }
    dialog.close();
  }
</script>

<dialog
  {id}
  class="m-auto rounded-lg border-0 p-0 shadow-xl backdrop:bg-slate-950/50"
  bind:this={dialog}
  onclick={(e) => {
    if (e.target === dialog) dialog.close();
  }}
>
  <div class="w-full max-w-xl bg-slate-50 p-4">
    <div data-header class="flex items-center justify-between gap-2">
      <div>{title}</div>
      <button
        type="button"
        class="flex size-8 items-center justify-center rounded-full bg-transparent p-1 text-center text-xl hover:cursor-pointer hover:bg-slate-950/15"
        title="Fechar"
        aria-label="Fechar Pop-up"
        onclick={() => dialog?.close()}
      >
        &times;
      </button>
    </div>
    <div data-body></div>
    <div data-footer></div>
  </div>
</dialog>
