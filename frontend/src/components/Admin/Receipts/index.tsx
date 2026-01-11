import { ReceiptService } from "@/client";
import { DataTable } from "@/components/Common/DataTable";
import SearchBar from "@/components/Common/SearchBar";
import PendingUsers from "@/components/Pending/PendingUsers";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Suspense, useState } from "react";
import { receiptColumns } from "../receiptColumns";

function getReceiptsSearchQueryOptions(searchQuery: string) {
  return {
    queryKey: ["receipts-search", searchQuery],
    queryFn: () =>
      ReceiptService.readReceipts({
        skip: 0,
        limit: 100,
        q: searchQuery || undefined,
      }),
  };
}

function ReceiptsTableContent() {
  const [searchQuery, setSearchQuery] = useState(""); // What we actually search for

  const { data: receipts } = useSuspenseQuery(
    getReceiptsSearchQueryOptions(searchQuery),
  );

  return (
    <div className="flex flex-col gap-4">
      <SearchBar
        placeholder="Pretraži račune..."
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />
      {receipts.data.length > 0 ? (
        <>
          <p className="text-sm text-muted-foreground">
            Pronađeno {receipts.count} računa
          </p>
          <DataTable columns={receiptColumns} data={receipts.data} />
        </>
      ) : (
        <p className="text-center text-muted-foreground py-8">
          Nema rezultata. Pokušajte drugu pretragu.
        </p>
      )}
    </div>
  );
}

function ReceiptsTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <ReceiptsTableContent />
    </Suspense>
  );
}

function Receipts() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Računi</h2>
        <p className="text-muted-foreground">
          Pretražite račune po korisniku, artiklu ili datumu
        </p>
      </div>
      <ReceiptsTable />
    </div>
  );
}

export default Receipts;
