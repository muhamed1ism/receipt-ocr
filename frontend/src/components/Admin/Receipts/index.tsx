import { ReceiptService } from "@/client";
import { DataTable } from "@/components/Common/DataTable";
import SearchBar from "@/components/Common/SearchBar";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Suspense, useState } from "react";
import { columns } from "./columns";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import PendingReceiptsTable from "@/components/Pending/PendingReceiptsTable";

function getReceiptsWithQuery(query: string) {
  return {
    queryKey: ["receipts-search", query],
    queryFn: () =>
      ReceiptService.readReceipts({
        skip: 0,
        limit: 30,
        q: query || undefined,
      }),
  };
}

function ReceiptsTableContent({ searchQuery }: { searchQuery: string }) {
  const {
    data: receipts,
    isError,
    error,
  } = useSuspenseQuery(getReceiptsWithQuery(searchQuery));

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

function ReceiptsTable({ query }: { query: string }) {
  return (
    <Suspense fallback={<PendingReceiptsTable />}>
      <ReceiptsTableContent searchQuery={query} />
    </Suspense>
  );
}

function Receipts() {
  const [query, setQuery] = useState(""); // What we actually search for
  const [inputValue, setInputValue] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setQuery(inputValue);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col lg:flex-row items-end justify-between gap-2 lg:gap-6">
        <div className="self-start">
          <h2 className="text-2xl font-bold tracking-tight">Računi</h2>
          <p className="text-muted-foreground">
            Pretražite račune po korisniku, artiklu ili datumu
          </p>
        </div>
        <div className="flex flex-row items-center grow w-full lg:w-fit gap-4">
          <SearchBar
            inputClassName="bg-background"
            placeholder="Pretraži račune..."
            searchQuery={inputValue}
            setSearchQuery={setInputValue}
            onKeyDown={handleKeyDown}
          />
          <Button className="rounded-sm" onClick={() => setQuery(inputValue)}>
            <Search />
          </Button>
        </div>
      </div>
      <ReceiptsTable query={query} />
    </div>
  );
}

export default Receipts;
