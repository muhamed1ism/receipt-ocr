import { ReceiptPublicDetailedMe } from "@/client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface ViewReceiptDialogProps {
  receipt: ReceiptPublicDetailedMe | null;
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
          <DialogTitle>Detalji računa {receipt?.branch.store.name}</DialogTitle>
          <DialogDescription>Pregled detalja vašeg računa </DialogDescription>
        </DialogHeader>
        {receipt && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              <div className="text-sm text-muted-foreground">Prodavnica:</div>
              <div className="text-sm font-medium">
                {receipt.branch.store.name}
              </div>

              <div className="text-sm text-muted-foreground">Datum:</div>
              <div className="text-sm font-medium">{receipt.date_time}</div>

              <div className="text-sm text-muted-foreground">Vrijeme:</div>
              <div className="text-sm font-medium">{receipt.date_time}</div>

              <div className="text-sm text-muted-foreground">Kategorija:</div>
              <div className="text-sm font-medium">KATEGORIJA</div>

              <div className="text-sm text-muted-foreground">Ukupno:</div>
              <div className="text-lg font-bold">{receipt.total_amount} KM</div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
