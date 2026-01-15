import { UsersService } from "@/client";
import PostRegister from "@/features/postRegister";
import { queryClient } from "@/lib/query";
import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/post-register")({
  component: PostRegister,
  beforeLoad: async () => {
    const user = await queryClient.ensureQueryData({
      queryKey: ["currentUser"],
      queryFn: UsersService.readUserMe,
    });

    if (user.profile !== null) {
      throw redirect({
        to: "/",
      });
    }
  },
});
