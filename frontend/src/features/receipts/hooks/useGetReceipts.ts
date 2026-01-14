import { ReceiptService } from "@/client";

const useGetReceipts = (query: string) => {
  return {
    queryKey: ["receipts-me-search", query],
    queryFn: () =>
      ReceiptService.readReceiptsMe({
        skip: 0,
        limit: 30,
        q: query || undefined,
      }),
  };
};

export default useGetReceipts;
