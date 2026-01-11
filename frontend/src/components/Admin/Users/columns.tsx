import type { ColumnDef } from "@tanstack/react-table"

import type { UserPublicWithProfile } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublicWithProfile & {
  isCurrentUser: boolean
}

export const columns: ColumnDef<UserTableData>[] = [
  {
    accessorKey: "first_name",
    header: "Ime",
    cell: ({ row }) => {
      const first_name = row.original.profile?.first_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "font-semibold",
              !first_name && "text-muted-foreground",
            )}
          >
            {first_name || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="secondary" className="text-xs font-semibold">
              Ti
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "last_name",
    header: "Prezime",
    cell: ({ row }) => {
      const last_name = row.original.profile?.last_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "font-semibold",
              !last_name && "text-muted-foreground",
            )}
          >
            {last_name || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="secondary" className="text-xs font-semibold">
              Ti
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "email",
    header: "Email",
    cell: ({ row }) => (
      <span className="text-muted-foreground font-semibold">
        {row.original.email}
      </span>
    ),
  },
  {
    accessorKey: "is_superuser",
    header: "Uloga",
    cell: ({ row }) => (
      <Badge
        className="font-semibold"
        variant={row.original.is_superuser ? "default" : "secondary"}
      >
        {row.original.is_superuser ? "Superkorisnik" : "Korisnik"}
      </Badge>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <div className="flex items-center gap-2 font-semibold">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_active ? "bg-green-500" : "bg-gray-400",
          )}
        />
        <span className={row.original.is_active ? "" : "text-muted-foreground"}>
          {row.original.is_active ? "Aktivan" : "Neaktivan"}
        </span>
      </div>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Akcije</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu user={row.original} />
      </div>
    ),
  },
]
