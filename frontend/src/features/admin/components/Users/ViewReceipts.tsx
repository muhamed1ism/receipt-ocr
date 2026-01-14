import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Eye } from "lucide-react";
import { useState } from "react";

function ViewReceipts() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <DropdownMenuItem
          onSelect={(e) => e.preventDefault()}
          onClick={() => setIsOpen(true)}
          className="font-receipt font-semibold"
        >
          <Eye />
          Pregled računa
        </DropdownMenuItem>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md font-receipt">
        <DialogHeader>
          <DialogTitle>Pregled računa korisnika</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          Neki opis za pregled svih računa korisnika
        </DialogDescription>
      </DialogContent>
    </Dialog>
  );
}

export default ViewReceipts;
