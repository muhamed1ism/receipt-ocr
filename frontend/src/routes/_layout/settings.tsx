import { createFileRoute } from "@tanstack/react-router";

import UserSettings from "@/features/settings";

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
});
