import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ViewReceiptDialog } from "@/components/Receipt/ViewReceiptDiolog";
import { ArrowDownWideNarrow, Grid2x2, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReceiptCard } from "@/components/Common/ReceiptCard";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import SearchBar from "@/components/Common/SearchBar";
import { MOCK_RECEIPTS } from "@/mock/receipts";
import { ReceiptPublicDetailedMe } from "@/client";
import { formatDate, formatTime } from "@/utils/formatDateTime";

export const Route = createFileRoute("/_layout/receipts")({
  component: Receipts,
});

interface modalType {
  isOpen: boolean;
  receipt: ReceiptPublicDetailedMe | null;
}

type ViewMode = "grid" | "list";

function Receipts() {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [searchQuery, setSearchQuery] = useState("");
  const [modal, setModal] = useState<modalType>({
    isOpen: false,
    receipt: null,
  });

  const receipts = MOCK_RECEIPTS;

  const groupedReceipts = receipts.data.reduce(
    (groups, receipt) => {
      const date = formatDate(receipt.date_time);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(receipt);
      return groups;
    },
    {} as Record<string, typeof receipts.data>,
  );

  const sortedDates = Object.keys(groupedReceipts).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime(),
  );

  sortedDates.forEach((date) => {
    groupedReceipts[date].sort((a, b) =>
      b.date_time.localeCompare(a.date_time),
    );
  });

  const handleOpenReceipt = (receipt: ReceiptPublicDetailedMe) => {
    setModal({ isOpen: true, receipt });
  };

  return (
    <section className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-4xl font-semibold">Svi Računi</h1>
        <div className="flex items-center">
          <SearchBar
            className="mr-4 rounded-xl"
            placeholder="Pretraži račune..."
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
          <Button variant="secondary" className="mr-4">
            <ArrowDownWideNarrow />
          </Button>
          <Button
            onClick={() => setViewMode("list")}
            variant={viewMode === "list" ? "default" : "secondary"}
            className="rounded-r-none"
          >
            <List />
          </Button>
          <Button
            onClick={() => setViewMode("grid")}
            variant={viewMode === "grid" ? "default" : "secondary"}
            className="rounded-l-none"
          >
            <Grid2x2 />
          </Button>
        </div>
      </div>

      {/* Display receipts */}
      {receipts.count === 0 ? (
        <ReceiptCard>
          <Card className="h-full rounded-none border-y-0">
            <p className="text-muted-foreground text-center">Nema računa</p>
          </Card>
        </ReceiptCard>
      ) : (
        <CardContent>
          {sortedDates.map((date) => (
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
                {groupedReceipts[date].map((receipt) =>
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
                          <p className="font-semibold">{receipt.branch.city}</p>
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
        </CardContent>
      )}
      <ViewReceiptDialog
        receipt={modal.receipt}
        onClose={() => setModal({ isOpen: false, receipt: null })}
      />
    </section>
  );
}
