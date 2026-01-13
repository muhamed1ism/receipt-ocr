import { ProfileService, ProfileUpdate } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const useEditProfile = (userId: string) => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: ProfileUpdate) =>
      ProfileService.updateProfile({ userId, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Profil je uspješno ažuriran");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useEditProfile;
