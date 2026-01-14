import { EllipsisVertical } from "lucide-react";
import { useState } from "react";

import type { UserPublicWithProfile } from "@/client";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import useAuth from "@/hooks/useAuth";
import ViewReceipts from "./ViewReceipts";
import EditProfile from "./Profile/EditProfile";
import AddProfile from "./Profile/AddProfile";
import EditUser from "./User/EditUser";
import DeleteUser from "./User/DeleteUser";

interface UserActionsMenuProps {
  user: UserPublicWithProfile;
}

export const UserActionsMenu = ({ user }: UserActionsMenuProps) => {
  const [open, setOpen] = useState(false);
  const { user: currentUser } = useAuth();

  if (user.id === currentUser?.id) {
    return null;
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <ViewReceipts />
        {user.profile ? (
          <EditProfile
            userId={user.id}
            profile={user.profile}
            onSuccess={() => setOpen(false)}
          />
        ) : (
          <AddProfile userId={user.id} />
        )}
        <EditUser user={user} onSuccess={() => setOpen(false)} />
        <DeleteUser id={user.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
