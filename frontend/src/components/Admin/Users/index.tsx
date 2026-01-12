import { UserPublicWithProfile, UsersService } from "@/client";
import useAuth from "@/hooks/useAuth";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Suspense, useState } from "react";
import { DataTable } from "@/components/Common/DataTable";
import PendingUsersTable from "@/components/Pending/PendingUsersTable";
import AddUser from "./AddUser";
import { columns, UserTableData } from "./columns";
import SearchBar from "@/components/Common/SearchBar";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

function getUsersQueryOptions(query: string) {
  return {
    queryKey: ["users", query],
    queryFn: () =>
      UsersService.readUsers({
        skip: 0,
        limit: 30,
        q: query || undefined,
      }),
  };
}

function UsersTableContent({ searchQuery }: { searchQuery: string }) {
  const { user: currentUser } = useAuth();
  const {
    data: users,
    isError,
    error,
  } = useSuspenseQuery(getUsersQueryOptions(searchQuery));

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

function UsersTable({ query }: { query: string }) {
  return (
    <Suspense fallback={<PendingUsersTable />}>
      <UsersTableContent searchQuery={query} />
    </Suspense>
  );
}

function Users() {
  const [query, setQuery] = useState("");
  const [inputValue, setInputValue] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setQuery(inputValue);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col lg:flex-row items-end justify-between gap-2 lg:gap-6">
        <div className="self-start">
          <h1 className="text-2xl font-bold tracking-tight">Korisnici</h1>
          <p className="text-muted-foreground">
            Upravljajte korisničkim računima i dozvolama
          </p>
        </div>
        <div className="flex items-center flex-row grow w-full lg:w-fit gap-4">
          <SearchBar
            inputClassName="bg-background"
            placeholder="Pretraži korisnike..."
            searchQuery={inputValue}
            setSearchQuery={setInputValue}
            onKeyDown={handleKeyDown}
          />

          <Button className="rounded-sm" onClick={() => setQuery(inputValue)}>
            <Search />
          </Button>
          <AddUser />
        </div>
      </div>
      <UsersTable query={query} />
    </div>
  );
}

export default Users;
