import { LoginService } from "@/client";
import { handleError } from "@/utils";
import { useMutation } from "@tanstack/react-query";
import { RecoverPasswordFormData } from "../schemas/authSchema";
import useCustomToast from "@/hooks/useCustomToast";

const recoverPassword = async (data: RecoverPasswordFormData) => {
  await LoginService.recoverPassword({
    email: data.email,
  });
};

const useRecoverPassword = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: recoverPassword,
    onSuccess: () => {
      showSuccessToast("Password recovery email sent successfully");
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useRecoverPassword;
