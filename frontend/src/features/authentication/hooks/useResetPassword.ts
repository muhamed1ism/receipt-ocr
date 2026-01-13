import { LoginService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

const useResetPassword = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: { new_password: string; token: string }) =>
      LoginService.resetPassword({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully");
      navigate({ to: "/login" });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useResetPassword;
