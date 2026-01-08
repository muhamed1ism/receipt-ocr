import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface Receipt {
  id: string;
  store: string;
  date: string;
  time: string;
  total: number;
  category: string;
}

interface ViewReceiptDialogProps {
  receipt: Receipt | null;
  onClose: () => void;
}

export function ViewReceiptDialog({
  receipt,
  onClose,
}: ViewReceiptDialogProps) {
  return (
    <Dialog open={receipt !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{receipt?.store} Receipt Details</DialogTitle>
          <DialogDescription>
            View the details of your receipt
          </DialogDescription>
        </DialogHeader>
        {receipt && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              <div className="text-sm text-muted-foreground">Prodavnica:</div>
              <div className="text-sm font-medium">{receipt.store}</div>

              <div className="text-sm text-muted-foreground">Datum:</div>
              <div className="text-sm font-medium">{receipt.date}</div>

              <div className="text-sm text-muted-foreground">Vrijeme:</div>
              <div className="text-sm font-medium">{receipt.time}</div>

              <div className="text-sm text-muted-foreground">Kategorija:</div>
              <div className="text-sm font-medium">{receipt.category}</div>

              <div className="text-sm text-muted-foreground">Ukupno:</div>
              <div className="text-lg font-bold">{receipt.total} KM</div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
