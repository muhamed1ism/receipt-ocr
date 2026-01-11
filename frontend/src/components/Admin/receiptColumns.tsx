import type { ColumnDef } from "@tanstack/react-table"
import type { ReceiptPublicDetailed } from "@/client"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/utils/formatDateTime"

export const receiptColumns: ColumnDef<ReceiptPublicDetailed>[] = [
  {
    accessorKey: "date_time",
    header: "Date",
    cell: ({ row }) => {
      const date = row.original.date_time
      return date ? formatDate(new Date(date)) : "N/A"
    },
  },
  {
    id: "user",
    header: "User",
    cell: ({ row }) => {
      const user = row.original.user
      if (!user?.profile) return user?.email || "N/A"
      return `${user.profile.first_name} ${user.profile.last_name}`
    },
  },
  {
    id: "store",
    header: "Store",
    cell: ({ row }) => {
      const branch = row.original.branch
      return branch?.store?.name || "N/A"
    },
  },
  {
    id: "items",
    header: "Items",
    cell: ({ row }) => {
      const items = row.original.items || []
      if (items.length === 0) return "No items"
      if (items.length === 1) return items[0].name
      return `${items[0].name} +${items.length - 1} more`
    },
  },
  {
    accessorKey: "total_amount",
    header: "Total",
    cell: ({ row }) => {
      const amount = row.original.total_amount
      const currency = row.original.currency || "BAM"
      return amount ? `${amount.toFixed(2)} ${currency}` : "N/A"
    },
  },
  {
    id: "actions",
    header: "Actions",
    cell: () => {
      // Add view details button/dialog here
      return <Badge variant="outline">View</Badge>
    },
  },
]
