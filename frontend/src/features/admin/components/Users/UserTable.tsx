import { Suspense } from "react";
import PendingUsersTable from "./PendingUsersTable";
import UsersTableContent from "./UserTableContent";

export default function UsersTable({ query }: { query: string }) {
  return (
    <Suspense fallback={<PendingUsersTable />}>
      <UsersTableContent searchQuery={query} />
    </Suspense>
  );
}
