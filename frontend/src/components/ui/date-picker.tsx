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
  const date = dateValue ? new Date(dateValue) : new Date();

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger className="hover:shadow-none" asChild>
        <Button
          variant="ghost"
          id="date"
          className={`flex min-w-36 w-full bg-transparent font-sans dark:bg-accent justify-between rounded-none border-b-2 border-dashed border-foreground/50 data-[state=open]:border-foreground hover:bg-transparent ${className}`}
        >
          {dateValue ? formatDate(dateValue) : "Odaberi datum"}
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
          onSelect={(value) => {
            if (!value) {
              setOpen(false);
              return;
            }
            value.setHours(date.getHours());
            value.setMinutes(date.getMinutes());
            setDateValue(value.toISOString());
            setOpen(false);
          }}
        />
      </PopoverContent>
    </Popover>
  );
}
