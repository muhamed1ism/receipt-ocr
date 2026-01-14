import { ProfileCreate, ProfileService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const useAddProfile = (userId: string) => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: ProfileCreate) =>
      ProfileService.createProfile({ userId, requestBody: data }),
    onSuccess: (_, _variables, _context) => {
      showSuccessToast("Profil je uspješno kreiran");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useAddProfile;
