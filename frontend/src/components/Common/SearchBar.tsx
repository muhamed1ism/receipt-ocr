import { Search } from "lucide-react";
import type { Dispatch, SetStateAction } from "react";
import { Input } from "../ui/input";

interface SearchBarType {
  className?: string;
  inputClassName?: string;
  placeholder?: string;
  searchQuery: string;
  setSearchQuery: Dispatch<SetStateAction<string>>;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

export default function SearchBar({
  className,
  inputClassName,
  placeholder = "Pretraži...",
  searchQuery,
  setSearchQuery,
  onKeyDown,
}: SearchBarType) {
  const searchClass = "relative w-full flex-1 " + className;
  const inputClass = "h-9 pl-10 bg-card " + inputClassName;

  return (
    <div className={searchClass}>
      <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
      <Input
        placeholder={placeholder}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className={inputClass}
        onKeyDown={onKeyDown}
      />
    </div>
  );
}
