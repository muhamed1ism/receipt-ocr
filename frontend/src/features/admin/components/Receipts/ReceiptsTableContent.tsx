import { useSuspenseQuery } from "@tanstack/react-query";
import useGetReceipts from "../../hooks/useGetReceipts";
import { DataTable } from "@/components/Common/DataTable";
import { columns } from "./columns";

export default function ReceiptsTableContent({
  searchQuery,
}: {
  searchQuery: string;
}) {
  const {
    data: receipts,
    isError,
    error,
  } = useSuspenseQuery(useGetReceipts({ query: searchQuery }));

  return (
    <div className="flex flex-col gap-4">
      {isError ? (
        <p className="text-center text-muted-foreground py-8">
          {error.message}
        </p>
      ) : receipts.count > 0 ? (
        <>
          <p className="text-sm text-muted-foreground">
            Pronađeno {receipts.count} računa
          </p>
          <DataTable columns={columns} data={receipts.data} />
        </>
      ) : (
        <p className="text-center text-muted-foreground py-8">
          Nema rezultata. Pokušajte drugu pretragu.
        </p>
      )}
    </div>
  );
}
