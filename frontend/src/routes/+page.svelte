<script lang="ts">
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
</script>

{#each data.posts as post}
  <article>
    <a href="/user/{post.author.id}/post">{post.author.username}</a>
    <a href="/post/{post.id}">{post.title}</a>
    <p>{post.content}</p>
    <small>{post.date_posted}</small>
  </article>
{/each}
