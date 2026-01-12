import { ReceiptCard } from "../Common/ReceiptCard";
import { Card, CardContent, CardFooter, CardHeader } from "../ui/card";
import { Skeleton } from "../ui/skeleton";

interface PendingReceiptsProps {
  viewMode: string;
}

const PendingReceipts = ({ viewMode }: PendingReceiptsProps) => (
  <>
    <h2 className="text-lg font-semibold mb-3 tracking-tighter">
      <Skeleton className="h-6 w-34 bg-foreground/10" />
    </h2>

    {viewMode === "grid"
      ? [...Array(8)].map((_, index) => (
          <ReceiptCard>
            <Card className="rounded-none border-y-0 h-full">
              <CardHeader className="flex flex-col items-center mb-1">
                <Skeleton className="h-6 w-40 mb-2" />
                <Skeleton className="h-4 w-30" />
                <Skeleton className="h-4 w-12" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-30 mb-2" />
                <Skeleton className="h-4 w-40 mb-1" />
              </CardContent>
              <CardFooter className="justify-center">
                <Skeleton className="h-6 w-22" />
              </CardFooter>
            </Card>
          </ReceiptCard>
        ))
      : [...Array(8)].map((_, index) => (
          <ReceiptCard>
            <Card className="rounded-none bg-card border-0 h-full flex flex-row justify-between items-start">
              <CardHeader className="min-w-[40%]">
                <Skeleton className="h-6 mb-3" />
                <Skeleton className="h-4 w-30" />
                <Skeleton className="h-4 w-12" />
              </CardHeader>
              <CardContent className="flex flex-col gap-2 items-end">
                <Skeleton className="h-5 w-50" />
                <Skeleton className="h-5 w-40 mb-1" />
                <Skeleton className="h-7 w-22" />
              </CardContent>
            </Card>
          </ReceiptCard>
        ))}
  </>
);

export default PendingReceipts;
