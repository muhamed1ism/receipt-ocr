import AddReceipt from "@/features/addReceipt";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_layout/add-receipt")({
  component: AddReceipt,
});
