import { createFileRoute } from "@tanstack/react-router";
import Receipts from "@/features/receipts";

export const Route = createFileRoute("/_layout/receipts")({
  component: Receipts,
});
