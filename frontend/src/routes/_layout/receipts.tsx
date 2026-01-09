import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ViewReceiptDialog } from "@/components/Receipt/ViewReceiptDiolog";
import { Grid2x2, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReceiptCard } from "@/components/Common/ReceiptCard";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const MOCK_RECEIPTS = [
  {
    id: "1",
    store: "Konzum",
    date: "2024-01-15",
    time: "14:30",
    total: 45.67,
    category: "Dućan",
  },
  {
    id: "4",
    store: "Konzum",
    date: "2024-01-15",
    time: "09:20",
    total: 78.9,
    category: "Dućan",
  },
  {
    id: "2",
    store: "Bingo",
    date: "2024-01-14",
    time: "10:15",
    total: 123.45,
    category: "Dućan",
  },
  {
    id: "5",
    store: "DM",
    date: "2024-01-14",
    time: "16:45",
    total: 67.89,
    category: "Drogerija",
  },
  {
    id: "6",
    store: "Song",
    date: "2024-01-14",
    time: "12:30",
    total: 420,
    category: "Restoran",
  },
  {
    id: "3",
    store: "Bingo",
    date: "2024-01-13",
    time: "10:15",
    total: 55.0,
    category: "Dućan",
  },
];

export const Route = createFileRoute("/_layout/receipts")({
  component: Receipts,
});

type ViewMode = "grid" | "list";

function Receipts() {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const receipts = MOCK_RECEIPTS;
  const [selectedReceipt, setSelectedReceipt] = useState<
    (typeof MOCK_RECEIPTS)[0] | null
  >(null);

  const groupedReceipts = receipts.reduce(
    (groups, receipt) => {
      const date = receipt.date;
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(receipt);
      return groups;
    },
    {} as Record<string, typeof MOCK_RECEIPTS>
  );

  const sortedDates = Object.keys(groupedReceipts).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  );

  sortedDates.forEach((date) => {
    groupedReceipts[date].sort((a, b) => b.time.localeCompare(a.time));
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="mb-2 mr-2 flex justify-end gap-3">
        <Button
          onClick={() => setViewMode("list")}
          className={viewMode === "list" ? "rounded" : "rounded bg-accent"}
        >
          <List />
        </Button>
        <Button
          onClick={() => setViewMode("grid")}
          className={viewMode === "grid" ? "rounded" : "rounded bg-accent"}
        >
          <Grid2x2 />
        </Button>
      </div>
      <ReceiptCard>
        <Card className="rounded-none border-y-0 h-full">
          <CardHeader className="mt-2">
            <CardTitle className="text-2xl font-bold tracking-tight">Svi Računi</CardTitle>
          </CardHeader>
          <div className="mt-2 border-b-2 border-dashed border-muted-foreground" />
          {/* Display receipts */}
          {receipts.length === 0 ? (
            <Card>
              <p className="text-muted-foreground">Nema računa</p>
            </Card>
          ) : (
            <CardContent>
              {sortedDates.map((date) => (
                <div
                  key={date}
                  className="mb-6 border-dashed border-b-2 border-foreground/50 pb-4"
                >
                  {/* Date Header */}
                  <h2 className="text-lg font-semibold mb-2">{date}</h2>
                  {/* viewMode*/}
                  <div
                    className={
                      viewMode === "grid"
                        ? "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-5"
                        : "flex flex-col gap-2"
                    }
                  >
                    {groupedReceipts[date].map((receipt) =>
                      viewMode === "grid" ? (
                        <ReceiptCard
                          key={receipt.id}
                          className="cursor-pointer hover:opacity-90 transition-opacity"
                        >
                          <Card
                            className="rounded-none border-y-0 h-full"
                            onClick={() => setSelectedReceipt(receipt)}
                          >
                            <CardHeader className="text-center">
                              <CardTitle className="text-base">
                                {receipt.store}
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="text-center text-sm text-muted-foreground space-y-1">
                              <p>{receipt.category}</p>
                              <p>{receipt.time}</p>
                            </CardContent>
                            <CardFooter className="justify-center">
                              <p className="font-bold text-lg">
                                {receipt.total} KM
                              </p>
                            </CardFooter>
                          </Card>
                        </ReceiptCard>
                      ) : (
                        <ReceiptCard
                          key={receipt.id}
                          className="cursor-pointer hover:opacity-90 transition-opacity"
                        >
                          <Card
                            className="rounded-none border-y-0 h-full"
                            onClick={() => setSelectedReceipt(receipt)}
                          >
                            <CardContent className="flex justify-between items-center">
                              <div>
                                <p className="font-semibold">{receipt.store}</p>
                                <p className="text-sm text-muted-foreground">
                                  {receipt.category}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                  {receipt.time}
                                </p>
                              </div>
                              <p className="font-bold">{receipt.total} KM</p>
                            </CardContent>
                          </Card>
                        </ReceiptCard>
                      )
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          )}
        </Card>
      </ReceiptCard>
      <ViewReceiptDialog
        receipt={selectedReceipt}
        onClose={() => setSelectedReceipt(null)}
      />
    </div>
  );
}
