import { ReceiptPublicDetailed } from "@/client";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EllipsisVertical } from "lucide-react";
import { useState } from "react";

interface ReceiptActionsMenuProps {
  receipt: ReceiptPublicDetailed;
}

export const ReceiptActionsMenu = ({ receipt }: ReceiptActionsMenuProps) => {
  const [open, setOpen] = useState(false);

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <Button>View</Button>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
