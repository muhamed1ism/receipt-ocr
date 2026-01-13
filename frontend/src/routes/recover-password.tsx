import RecoverPassword from "@/features/authentication/recover-password";
import { isLoggedIn } from "@/hooks/useAuth";
import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/recover-password")({
  component: RecoverPassword,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      });
    }
  },
});
