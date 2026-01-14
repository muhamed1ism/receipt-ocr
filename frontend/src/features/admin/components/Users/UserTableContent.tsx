import { UserPublicWithProfile } from "@/client";
import { DataTable } from "@/components/Common/DataTable";
import useAuth from "@/hooks/useAuth";
import { useSuspenseQuery } from "@tanstack/react-query";
import useGetUsers from "../../hooks/useGetUsers";
import { UserTableData, columns } from "./columns";

export default function UsersTableContent({
  searchQuery,
}: {
  searchQuery: string;
}) {
  const { user: currentUser } = useAuth();
  const {
    data: users,
    isError,
    error,
  } = useSuspenseQuery(useGetUsers({ query: searchQuery }));

  const tableData: UserTableData[] = users.data.map(
    (user: UserPublicWithProfile) => ({
      ...user,
      isCurrentUser: currentUser?.id === user.id,
    }),
  );

  return (
    <div className="flex flex-col gap-4">
      {isError ? (
        <p className="text-center text-muted-foreground py-8">
          {error.message}
        </p>
      ) : users.count > 0 ? (
        <>
          <p className="text-sm text-muted-foreground">
            Pronađeno {users.count} računa
          </p>
          <DataTable columns={columns} data={tableData} />
        </>
      ) : (
        <p className="text-center text-muted-foreground py-8">
          Nema rezultata. Pokušajte drugu pretragu.
        </p>
      )}
    </div>
  );
}
