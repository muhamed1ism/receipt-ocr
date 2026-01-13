import { createFileRoute, redirect } from "@tanstack/react-router";
import { z } from "zod";

import { isLoggedIn } from "@/hooks/useAuth";
import ResetPassword from "@/features/authentication/reset-password";

const searchSchema = z.object({
  token: z.string().catch(""),
});

export const Route = createFileRoute("/reset-password")({
  component: ResetPassword,
  validateSearch: searchSchema,
  beforeLoad: async ({ search }) => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" });
    }
    if (!search.token) {
      throw redirect({ to: "/login" });
    }
  },
});
