import PostRegister from "@/features/postRegister";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/post-register")({
  component: PostRegister,
});
