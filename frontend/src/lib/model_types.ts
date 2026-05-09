export interface UserPublic {
  id: number;
  username: string;
  image_file?: string;
  image_path: string;
}

export interface UserPrivate extends UserPublic {
  email: string;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  user_id: number;
  date_posted: Date;
  author: UserPublic;
}
