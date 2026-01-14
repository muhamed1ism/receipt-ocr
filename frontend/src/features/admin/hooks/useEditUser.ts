import { UsersService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { EditUserFormData } from "../schemas/userSchemas";

const useEditUser = (userId: string) => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: EditUserFormData) =>
      UsersService.updateUser({ userId, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Korisnik je uspješno ažuriran");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useEditUser;
