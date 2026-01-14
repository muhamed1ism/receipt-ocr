import SearchBar from "@/components/Common/SearchBar";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import ReceiptsTable from "./ReceiptsTable";

export default function Receipts() {
  const [query, setQuery] = useState(""); // What we actually search for
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
          <h2 className="text-2xl font-bold tracking-tight">Računi</h2>
          <p className="text-muted-foreground">
            Pretražite račune po korisniku, artiklu ili datumu
          </p>
        </div>
        <div className="flex flex-row items-center grow w-full lg:w-fit gap-4">
          <SearchBar
            inputClassName="bg-background"
            placeholder="Pretraži račune..."
            searchQuery={inputValue}
            setSearchQuery={setInputValue}
            onKeyDown={handleKeyDown}
          />
          <Button className="rounded-sm" onClick={() => setQuery(inputValue)}>
            <Search />
          </Button>
        </div>
      </div>
      <ReceiptsTable query={query} />
    </div>
  );
}
