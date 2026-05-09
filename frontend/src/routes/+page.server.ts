import type { Post } from "$lib/model_types";

const POSTS_URL = "http://localhost:8000/api/post";

export async function load() {
  try {
    const response = await fetch(POSTS_URL);
    if (!response.ok) {
      return { posts: [] };
    }
    const data: Array<Post> = await response.json();
    return {
      posts: data
    };
  } catch (error) {
    return { posts: [] };
  }
}
