import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ViewReceiptDialog } from "@/components/Receipt/ViewReceiptDiolog";

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

function Receipts() {

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
          <p className="text-muted-foreground">Pregled svih računa</p>
        </div>
      </div>

      {/* Display receipts */}
      {receipts.length === 0 ? (
        <div className="rounded-lg border p-8 text-center">
          <p className="text-muted-foreground">Nema računa</p>
        </div>
      ) : (
        <div className="rounded-lg border">
          <div className="p-4 space-y-4">
            {sortedDates.map((date) => (
              <div key={date}>
                {/* Date Header */}
                <h2 className="text-lg font-semibold mb-3">{date}</h2>

                {/* Receipts for that date */}
                <div className="rounded-lg border mb-6">
                  <div className="divide-y">
                    {groupedReceipts[date].map((receipt) => (
                      <div
                        key={receipt.id}
                        className="flex justify-between p-4 cursor-pointer hover:bg-accent hover:rounded transition-colors "
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
                        <p className="font-bold self-center">{receipt.total} KM</p>
                      </div>
                    ))}
                  </div>
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
