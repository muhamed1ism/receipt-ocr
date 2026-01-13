import { UserCreate, UsersService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const useAddUser = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: UserCreate) =>
      UsersService.createUser({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Korisnik je uspješno kreiran");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useAddUser;
