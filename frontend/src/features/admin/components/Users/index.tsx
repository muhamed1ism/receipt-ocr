import { useState } from "react";
import AddUser from "./User/AddUser";
import SearchBar from "@/components/Common/SearchBar";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import UsersTable from "./UserTable";

export default function Users() {
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
