import { Search } from "lucide-react";
import { Input } from "../ui/input";
import { Dispatch, SetStateAction } from "react";

interface SearchBarType {
  className?: string;
  placeholder?: string;
  searchQuery: string;
  setSearchQuery: Dispatch<SetStateAction<string>>;
}

export default function SearchBar({
  className,
  placeholder = "Pretraži...",
  searchQuery,
  setSearchQuery,
}: SearchBarType) {
  const searchClass = "relative w-full flex-1 " + className;

  return (
    <div className={searchClass}>
      <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
      <Input
        placeholder={placeholder}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="bg-card h-9 pl-10"
      />
    </div>
  );
}
