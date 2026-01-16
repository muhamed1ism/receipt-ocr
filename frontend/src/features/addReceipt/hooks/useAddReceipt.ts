import { ReceiptService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { AddReceiptFormValues } from "../schemas/receiptsShema";

const useAddReceipt = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: AddReceiptFormValues) =>
      ReceiptService.createReceipt({ requestBody: data }),
    onSuccess: (_, _variables, _context) => {
      showSuccessToast("Svaka čast pajdo");
      queryClient.invalidateQueries({ queryKey: ["receipts"] });
      navigate({ to: "/receipts" });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useAddReceipt;
