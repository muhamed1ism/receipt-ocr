import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useState } from "react"
import {
  ReceiptService,
  type UserPublicWithProfile,
  UsersService,
} from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { columns, type UserTableData } from "@/components/Admin/columns"
import { receiptColumns } from "@/components/Admin/receiptColumns"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"
import { Input } from "@/components/ui/input"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
})

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: ["users"],
  }
}

function getReceiptsSearchQueryOptions(searchQuery: string) {
  return {
    queryKey: ["receipts-search", searchQuery],
    queryFn: () =>
      ReceiptService.readReceipts({
        skip: 0,
        limit: 100,
        q: searchQuery || undefined,
      }),
  }
}

function ReceiptsTableContent() {
  const [inputValue, setInputValue] = useState("") // What user is typing
  const [searchQuery, setSearchQuery] = useState("") // What we actually search for

  const { data: receipts } = useSuspenseQuery(
    getReceiptsSearchQueryOptions(searchQuery),
  )

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setSearchQuery(inputValue)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="relative w-full flex-1">
        <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
        <Input
          placeholder="Pretraži račune... (pritisni Enter)"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="bg-card h-9 pl-10"
        />
      </div>
      {receipts.data.length > 0 ? (
        <>
          <p className="text-sm text-muted-foreground">
            Pronađeno {receipts.count} računa
          </p>
          <DataTable columns={receiptColumns} data={receipts.data} />
        </>
      ) : (
        <p className="text-center text-muted-foreground py-8">
          Nema rezultata. Pokušajte drugu pretragu.
        </p>
      )}
    </div>
  )
}

function ReceiptsTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <ReceiptsTableContent />
    </Suspense>
  )
}

function UsersTableContent() {
  const { user: currentUser } = useAuth()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const tableData: UserTableData[] = users.data.map(
    (user: UserPublicWithProfile) => ({
      ...user,
      isCurrentUser: currentUser?.id === user.id,
    }),
  )

  return <DataTable columns={columns} data={tableData} />
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  )
}

function Admin() {
  return (
    <div className="flex flex-col gap-10">
      {/* Korisnici section */}
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Korisnici</h1>
            <p className="text-muted-foreground">
              Upravljajte korisničkim računima i dozvolama
            </p>
          </div>
          <AddUser />
        </div>
        <UsersTable />
      </div>

      {/* Računi section - NEW */}
      <div className="flex flex-col gap-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Računi</h2>
          <p className="text-muted-foreground">
            Pretražite račune po korisniku, artiklu ili datumu
          </p>
        </div>
        <ReceiptsTable />
      </div>
    </div>
  )
}
