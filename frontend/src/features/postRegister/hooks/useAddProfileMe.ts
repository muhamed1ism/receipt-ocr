import { ProfileCreateMe, ProfileService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const useAddProfileMe = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: ProfileCreateMe) =>
      ProfileService.createProfileMe({ requestBody: data }),
    onSuccess: (_, _variables, _context) => {
      showSuccessToast("Profil je uspješno kreiran");
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      window.location.reload();
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useAddProfileMe;
