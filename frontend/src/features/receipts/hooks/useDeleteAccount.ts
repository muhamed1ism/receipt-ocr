import { UsersService } from "@/client";
import useAuth from "@/hooks/useAuth";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useQueryClient, useMutation } from "@tanstack/react-query";

const useDeleteAccount = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const { logout } = useAuth();

  return useMutation({
    mutationFn: () => UsersService.deleteUserMe(),
    onSuccess: () => {
      showSuccessToast("Vaš račun je uspješno obrisan.");
      logout();
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useDeleteAccount;
