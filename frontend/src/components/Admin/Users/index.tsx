import { UserPublicWithProfile, UsersService } from "@/client";
import useAuth from "@/hooks/useAuth";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Suspense, useState } from "react";
import { DataTable } from "@/components/Common/DataTable";
import PendingUsers from "@/components/Pending/PendingUsers";
import AddUser from "./AddUser";
import { columns, UserTableData } from "./columns";
import SearchBar from "@/components/Common/SearchBar";

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: ["users"],
  };
}

function UsersTableContent() {
  const { user: currentUser } = useAuth();
  const { data: users } = useSuspenseQuery(getUsersQueryOptions());

  const tableData: UserTableData[] = users.data.map(
    (user: UserPublicWithProfile) => ({
      ...user,
      isCurrentUser: currentUser?.id === user.id,
    }),
  );

  return <DataTable columns={columns} data={tableData} />;
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  );
}

function Users() {
  const [query, setQuery] = useState("");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col lg:flex-row items-center justify-between gap-2 lg:gap-6">
        <div className="self-start">
          <h1 className="text-2xl font-bold tracking-tight">Korisnici</h1>
          <p className="text-muted-foreground">
            Upravljajte korisničkim računima i dozvolama
          </p>
        </div>
        <SearchBar
          inputClassName="bg-background"
          placeholder="Pretraži korisnike..."
          searchQuery={query}
          setSearchQuery={setQuery}
        />
        <AddUser />
      </div>
      <UsersTable />
    </div>
  );
}

export default Users;
