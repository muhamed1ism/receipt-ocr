import { UserUpdateMe, UsersService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useQueryClient, useMutation } from "@tanstack/react-query";

const useChangeEmail = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Korisnik je uspješno ažuriran");
      queryClient.invalidateQueries();
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useChangeEmail;
