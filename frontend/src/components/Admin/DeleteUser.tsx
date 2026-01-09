import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { UsersService } from "@/client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { LoadingButton } from "@/components/ui/loading-button";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";

interface DeleteUserProps {
  id: string;
  onSuccess: () => void;
}

const DeleteUser = ({ id, onSuccess }: DeleteUserProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const { showSuccessToast, showErrorToast } = useCustomToast();
  const { handleSubmit } = useForm();

  const deleteUser = async (id: string) => {
    await UsersService.deleteUser({ userId: id });
  };

  const mutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      showSuccessToast("Korisnik je uspješno obrisan.");
      setIsOpen(false);
      onSuccess();
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries();
    },
  });

  const onSubmit = async () => {
    mutation.mutate(id);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
        className="font-receipt font-semibold"
      >
        <Trash2 />
        Obriši korisnika
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md font-receipt">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Obriši korisnika</DialogTitle>
            <DialogDescription>
              Svi predmeti povezani s ovim korisnikom će također biti{" "}
              <strong>trajno obrisani.</strong> Da li ste sigurni? Nećete moći
              opozvati ovu akciju.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button
                variant="outline"
                disabled={mutation.isPending}
                className="font-semibold"
              >
                Odustani
              </Button>
            </DialogClose>
            <LoadingButton
              variant="destructive"
              type="submit"
              loading={mutation.isPending}
              className="font-semibold"
            >
              Obriši
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default DeleteUser;
