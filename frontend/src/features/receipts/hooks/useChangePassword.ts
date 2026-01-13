import { UpdatePassword, UsersService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation } from "@tanstack/react-query";

const useChangePassword = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully");
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useChangePassword;
