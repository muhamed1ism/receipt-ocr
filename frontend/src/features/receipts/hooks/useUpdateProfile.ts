import { ProfileUpdate, ProfileService } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { useQueryClient, useMutation } from "@tanstack/react-query";

const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  return useMutation({
    mutationFn: (data: ProfileUpdate) =>
      ProfileService.updateProfileMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Profil je uspješno ažuriran");
      queryClient.invalidateQueries();
    },
    onError: handleError.bind(showErrorToast),
  });
};

export default useUpdateProfile;
