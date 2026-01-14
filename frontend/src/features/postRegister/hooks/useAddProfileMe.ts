import { ProfileCreateMe, ProfileService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

const useAddProfileMe = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: ProfileCreateMe) =>
      ProfileService.createProfileMe({ requestBody: data }),
    onSuccess: (_, _variables, _context) => {
      showSuccessToast("Profil je uspješno kreiran");
      queryClient.invalidateQueries({ queryKey: ["users"] });
      navigate({ to: "/" });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useAddProfileMe;
