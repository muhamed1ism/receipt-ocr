import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ViewReceiptDialog } from "@/components/Receipt/ViewReceiptDiolog";
import { Grid2x2, List } from "lucide-react";

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Svi Računi</h1>
        </div>
      </div>
      <div className="mb-2 mr-2 flex justify-end gap-3">
        <button
          onClick={() => setViewMode("list")}
          className={viewMode === "list" ? "bg-accent rounded p-2" : "p-2"}
        >
          <List />
        </button>
        <button
          onClick={() => setViewMode("grid")}
          className={viewMode === "grid" ? "bg-accent rounded p-2" : "p-2"}
        >
          <Grid2x2 />
        </button>
      </div>
      {/* Display receipts */}
      {receipts.length === 0 ? (
        <div className="rounded-lg border p-8 text-center">
          <p className="text-muted-foreground">Nema računa</p>
        </div>
      ) : (
        <div className="rounded-lg border-2 border-foreground/50">
          <div className="p-4 space-y-4">
            {sortedDates.map((date) => (
              <div key={date}
              className="mb-6 border-dashed border-b-2 border-foreground/50 pb-4 divide-y divide-foreground/50 lg:divide-y-0 md:divide-y-0 ">
                {/* Date Header */}
                <h2 className="text-lg font-semibold mb-2">{date}</h2>
                {/* viewMode*/}
                <div
                  className={
                    viewMode === "grid"
                      ? "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-5"
                      : "rounded-lg mb-6 divide-y divide-foreground/50 md:border-2 lg:border-2 border-foreground/50"
                  }
                >
                  {groupedReceipts[date].map((receipt) => (
                    <div
                      key={receipt.id}
                      className={
                        viewMode === "grid"
                          ? "rounded-lg border-2 border-foreground/50 p-4 cursor-pointer hover:bg-muted transition-colors text-center"
                          : "flex justify-between p-4 cursor-pointer hover:bg-muted hover:rounded transition-colors"
                      }
                      onClick={() => setSelectedReceipt(receipt)}
                    >
                      <div>
                        <p className="font-semibold">{receipt.store}</p>
                        <p className="text-sm text-muted-foreground">
                          {receipt.category}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {receipt.time}
                        </p>
                      </div>
                      <p className="font-bold self-center">
                        {receipt.total} KM
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <ViewReceiptDialog
        receipt={selectedReceipt}
        onClose={() => setSelectedReceipt(null)}
      />
    </div>
  );
}
