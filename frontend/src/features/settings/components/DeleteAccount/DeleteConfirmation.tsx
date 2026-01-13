import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { LoadingButton } from "@/components/ui/loading-button";
import useDeleteAccount from "@/features/receipts/hooks/useDeleteAccount";

const DeleteConfirmation = () => {
  const { handleSubmit } = useForm();

  const mutation = useDeleteAccount();
  const onSubmit = async () => {
    mutation.mutate();
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="destructive" className="mt-3 font-semibold">
          Obriši račun
        </Button>
      </DialogTrigger>
      <DialogContent className="font-receipt">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Potvrda je potrebna</DialogTitle>
            <DialogDescription>
              Svi podaci vašeg računa će biti <strong>trajno obrisani.</strong>{" "}
              Ako ste sigurni, kliknite <strong>"Potvrdi"</strong> da nastavite.
              Ova akcija se ne može opozvati.
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

export default DeleteConfirmation;
