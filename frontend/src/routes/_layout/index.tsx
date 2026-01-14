import { createFileRoute } from "@tanstack/react-router";
import Dashboard from "@/features/home";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
});
