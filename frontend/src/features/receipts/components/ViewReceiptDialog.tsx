import { XIcon } from "lucide-react";
import type { ReceiptPublicDetailedMe } from "@/client";
import { ReceiptCard } from "@/components/Common/ReceiptCard";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { formatDate, formatTime } from "@/utils/formatDateTime";

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
      <DialogContent
        className="font-receipt p-2 border-none bg-transparent shadow-none overflow-visible rounded-none"
        showCloseButton={false}
      >
        {receipt && (
          <ReceiptCard className="relative lg:text-lg">
            <Button
              onClick={onClose}
              variant="ghost"
              size="icon-sm"
              className="absolute top-6 right-6 z-10"
            >
              <XIcon />
              <span className="sr-only">Close</span>
            </Button>
            <Card className="rounded-none border-y-0 relative">
              <CardHeader className="pt-12">
                <CardTitle className="font-semibold text-center text-xl lg:text-2xl">
                  {receipt.branch.store.name}
                </CardTitle>
                <div className="mx-15 border-b-2 border-dashed border-muted-foreground mb-3" />
                <CardDescription>
                  <div className="flex justify-between w-full">
                    <p className="">{receipt.branch.city}</p>

                    <p className="">
                      {receipt.date_time
                        ? formatTime(receipt.date_time)
                        : "N/A"}
                    </p>
                  </div>
                  <div className="flex justify-between w-full">
                    <p className="">{receipt.branch.address}</p>
                    <p className="">
                      {receipt.date_time
                        ? formatDate(receipt.date_time)
                        : "N/A"}
                    </p>
                  </div>
                </CardDescription>
                <div className="mb-2 border-dashed border-b-2 border-foreground/50 pb-4" />
                <p className="text-muted-foreground">STAVKE NA RAČUNU</p>
              </CardHeader>
              <CardContent className="space-y-8">
                {receipt.items?.map((item) => (
                  <div key={item.id}>
                    <div className="flex justify-between w-full text-lg lg:text-xl">
                      <p className="font-medium">{item.name}</p>
                      <p className="text-right font-semibold hidden md:block">
                        {item.total_price.toFixed(2)} KM
                      </p>
                    </div>
                    <div className="flex flex-row justify-between">
                      <div className="flex gap-4 text-muted-foreground">
                        <p>{item.quantity}</p>
                        <p>x</p>
                        <p>{item.price.toFixed(2)} KM</p>
                      </div>
                      <p className="text-right font-semibold md:hidden block">
                        {item.total_price.toFixed(2)} KM
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>

              <CardFooter className="flex flex-col gap-0 items-stretch">
                <div className="border-b-2 border-dashed border-muted-foreground mb-3" />
                <div className="w-full flex justify-between mb-2 items-end text-muted-foreground">
                  <p>PDV:</p>
                  <p>
                    {receipt.tax_amount} KM

                  </p>
                </div>
                <div className="w-full flex justify-between mb-2 items-end">
                  <p className=" text-muted-foreground">Ukupno:</p>
                  <p className="text-2xl font-bold">
                    {receipt.total_amount} KM
                  </p>
                </div>
                <div className="mx-15 border-b-2 border-dashed border-muted-foreground my-3" />
                <div className="text-muted-foreground text-center">
                  <p>HVALA NA POSJETI!</p>
                  <p>Thank you for your visit!</p>
                </div>
              </CardFooter>
            </Card>
          </ReceiptCard>
        )}
      </DialogContent>
    </Dialog>
  );
}
