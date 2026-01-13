import PendingReceiptsTable from "@/components/Pending/PendingReceiptsTable";
import { Suspense } from "react";
import ReceiptsTableContent from "./ReceiptsTableContent";

export default function ReceiptsTable({ query }: { query: string }) {
  return (
    <Suspense fallback={<PendingReceiptsTable />}>
      <ReceiptsTableContent searchQuery={query} />
    </Suspense>
  );
}
