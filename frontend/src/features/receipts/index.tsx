import { ArrowDownWideNarrow, Grid2x2, List, Search } from "lucide-react";
import { Suspense, useState } from "react";
import { ReceiptService, type ReceiptPublicDetailedMe } from "@/client";
import { ReceiptCard } from "@/components/Common/ReceiptCard";
import SearchBar from "@/components/Common/SearchBar";
import { ViewReceiptDialog } from "@/components/Receipt/ViewReceiptDiolog";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDate, formatTime } from "@/utils/formatDateTime";
import { useSuspenseQuery } from "@tanstack/react-query";
import PendingReceipts from "@/components/Pending/PendingReceipts";

interface modalType {
  isOpen: boolean;
  receipt: ReceiptPublicDetailedMe | null;
}

type ViewMode = "grid" | "list";

function getReceiptsWithQuery(query: string) {
  return {
    queryKey: ["receipts-me-search", query],
    queryFn: () =>
      ReceiptService.readReceiptsMe({
        skip: 0,
        limit: 30,
        q: query || undefined,
      }),
  };
}

export default function Receipts() {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [query, setQuery] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [modal, setModal] = useState<modalType>({
    isOpen: false,
    receipt: null,
  });

  const { data: receipts } = useSuspenseQuery(getReceiptsWithQuery(query));

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setQuery(inputValue);
    }
  };

  const groupedByDate = receipts.data.reduce<
    Record<string, ReceiptPublicDetailedMe[]>
  >((acc, receipt) => {
    const dateKey = receipt.date_time.split("T")[0]; // YYYY-MM-DD
    (acc[dateKey] ??= []).push(receipt);
    return acc;
  }, {});

  const handleOpenReceipt = (receipt: ReceiptPublicDetailedMe) => {
    setModal({ isOpen: true, receipt });
  };

  return (
    <section className="flex flex-col gap-6">
      <div className="grid grid-cols-12 items-center">
        <h1 className="text-4xl font-semibold col-span-12 lg:col-span-6">
          Svi Računi
        </h1>
        <div className="flex items-center col-span-12 lg:col-span-6">
          <div className="flex flex-row items-center grow w-full lg:w-fit gap-4">
            <SearchBar
              placeholder="Pretraži račune..."
              searchQuery={inputValue}
              setSearchQuery={setInputValue}
              onKeyDown={handleKeyDown}
            />
            <Button className="rounded-sm" onClick={() => setQuery(inputValue)}>
              <Search />
            </Button>
            <Button variant="secondary" className="bg-card mr-4 rounded-sm">
              <ArrowDownWideNarrow />
            </Button>
          </div>
          <Button
            onClick={() => setViewMode("list")}
            variant={viewMode === "list" ? "default" : "secondary"}
            className={`rounded-r-none rounded-l-sm ${viewMode === "list" ? "" : "bg-card"}`}
          >
            <List />
          </Button>
          <Button
            onClick={() => setViewMode("grid")}
            variant={viewMode === "grid" ? "default" : "secondary"}
            className={`rounded-l-none rounded-r-sm ${viewMode === "grid" ? "" : "bg-card"}`}
          >
            <Grid2x2 />
          </Button>
        </div>
      </div>

      <Suspense fallback={<PendingReceipts viewMode={viewMode} />}>
        {/* Display receipts */}
        {receipts.count === 0 ? (
          <ReceiptCard>
            <Card className="h-full rounded-none border-y-0">
              <p className="text-muted-foreground text-center">Nema računa</p>
            </Card>
          </ReceiptCard>
        ) : (
          <div>
            {Object.entries(groupedByDate).map(([date, receipts]) => (
              <div
                key={date}
                className="mb-6 border-dashed border-b-2 border-foreground/50 pb-4"
              >
                {/* Date Header */}
                <h2 className="text-lg font-semibold mb-3 tracking-tighter">
                  {formatDate(date)}
                </h2>
                {/* viewMode*/}
                <div
                  className={
                    viewMode === "grid"
                      ? "grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-5"
                      : "flex flex-col gap-3"
                  }
                >
                  {receipts.map((receipt) =>
                    viewMode === "grid" ? (
                      <div key={receipt.id}>
                        {/* Grid View */}
                        <ReceiptCard
                          hoverShadow={true}
                          className="cursor-pointer transition-all duration-300 hover:scale-105"
                        >
                          <Card
                            className="rounded-none border-y-0 h-full"
                            onClick={() => handleOpenReceipt(receipt)}
                          >
                            <CardHeader className="text-center">
                              <CardTitle className="text-xl">
                                {receipt.branch.store.name}
                              </CardTitle>
                              <CardDescription className="text-center text-sm text-muted-foreground space-y-1">
                                <p>KATEGORIJA</p>
                                <p>{formatTime(receipt.date_time)}</p>
                              </CardDescription>
                            </CardHeader>
                            <CardContent>
                              <p className="font-semibold">
                                {receipt.branch.city}
                              </p>
                              <p>{receipt.branch.address}</p>
                            </CardContent>
                            <CardFooter className="justify-center">
                              <p className="font-bold text-2xl">
                                {receipt.total_amount} KM
                              </p>
                            </CardFooter>
                          </Card>
                        </ReceiptCard>
                      </div>
                    ) : (
                      <ReceiptCard
                        hoverShadow={true}
                        key={receipt.id}
                        className="cursor-pointer transition-all duration-300 hover:scale-105"
                      >
                        {/* List View */}
                        <Card
                          className="rounded-none border-y-0 h-full flex flex-row justify-between items-baseline"
                          onClick={() => handleOpenReceipt(receipt)}
                        >
                          <CardHeader className=" min-w-[40%]">
                            <CardTitle className="text-xl">
                              {receipt.branch.store.name}
                            </CardTitle>
                            <CardDescription>
                              <div className="text-sm text-muted-foreground">
                                <span>KATEGORIJA</span>
                                <p>{formatTime(receipt.date_time)}</p>
                              </div>
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="text-end">
                            <p className="font-semibold">
                              {receipt.branch.city}
                            </p>
                            <p>{receipt.branch.address}</p>
                            <p className="font-bold text-2xl">
                              {receipt.total_amount} KM
                            </p>
                          </CardContent>
                        </Card>
                      </ReceiptCard>
                    ),
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Suspense>
      <ViewReceiptDialog
        receipt={modal.receipt}
        onClose={() => setModal({ isOpen: false, receipt: null })}
      />
    </section>
  );
}
