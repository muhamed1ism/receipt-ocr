import { ReceiptService } from "@/client";

interface useGetReceiptsProps {
  query: string;
  limit?: number;
  skip?: number;
}

const useGetReceipts = ({
  query,
  limit = 30,
  skip = 0,
}: useGetReceiptsProps) => {
  return {
    queryKey: ["receipts-search", query],
    queryFn: () =>
      ReceiptService.readReceipts({
        skip,
        limit,
        q: query || undefined,
      }),
  };
};

export default useGetReceipts;
