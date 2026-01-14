import * as React from "react";
import { ChevronDownIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { bs } from "date-fns/locale";
import { formatDate } from "@/utils/formatDateTime";

interface DatePickerProps {
  dateValue: string;
  setDateValue: (date: string) => void;
  className?: string;
}

export function DatePicker({
  dateValue,
  setDateValue,
  className,
}: DatePickerProps) {
  const [open, setOpen] = React.useState(false);
  const date = new Date(dateValue);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          id="date"
          className={`flex bg-transparent font-sans dark:bg-accent justify-between rounded-none border-b-2 border-dashed border-foreground/50 data-[state=open]:border-foreground ${className}`}
        >
          {dateValue ? formatDate(dateValue) : "Select date"}
          <ChevronDownIcon />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto overflow-hidden p-0" align="start">
        <Calendar
          defaultMonth={date}
          weekStartsOn={1}
          locale={bs}
          mode="single"
          selected={date}
          captionLayout="dropdown"
          onSelect={(date) => {
            if (date) setDateValue(date?.toLocaleDateString("en-CA"));
            setOpen(false);
          }}
        />
      </PopoverContent>
    </Popover>
  );
}
