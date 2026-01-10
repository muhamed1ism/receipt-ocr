import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Suspense } from "react";

import { type UserPublic, UserPublicWithProfile, UsersService } from "@/client";
import AddUser from "@/components/Admin/AddUser";
import { columns, type UserTableData } from "@/components/Admin/columns";
import { DataTable } from "@/components/Common/DataTable";
import PendingUsers from "@/components/Pending/PendingUsers";
import useAuth from "@/hooks/useAuth";

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: ["users"],
  };
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
});

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

function Admin() {
  return (
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
  );
}
