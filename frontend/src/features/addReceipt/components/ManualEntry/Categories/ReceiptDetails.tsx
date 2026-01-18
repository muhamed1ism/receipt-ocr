import DynamicFormField from "@/components/Forms/DynamicFormField";
import { AddReceiptFormData } from "@/features/addReceipt/schemas/receiptsShema";
import { ChevronRight } from "lucide-react";
import { useState } from "react";
import { UseFormReturn } from "react-hook-form";

interface ReceiptDetailsProps {
  form: UseFormReturn<AddReceiptFormData>;
}

export default function ReceiptDetails({ form }: ReceiptDetailsProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="space-y-4 mt-2">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xl font-bold hover:text-muted-foreground"
      >
        <ChevronRight
          size={18}
          className={`transition-transform ${expanded ? "rotate-90" : ""}`}
        />
        Tehnički detalji
      </button>
      {expanded && (
        <div className="grid grid-cols-2 gap-8">
          <DynamicFormField
            control={form.control}
            name="store.jib"
            label="JIB - Jedinstveni identifikacijski broj"
            type="text"
          />
          <DynamicFormField
            control={form.control}
            name="store.pib"
            label="PIB - Poreski identifikacijski broj"
            type="text"
          />
          <DynamicFormField
            control={form.control}
            name="details.ibfm"
            label="IBFM - identifikacioni broj fiskalnog modula"
            type="text"
          />
          <DynamicFormField
            control={form.control}
            name="details.bf"
            label="BF - broj fiskalnog računa"
            type="number"
          />
          <DynamicFormField
            control={form.control}
            name="details.digital_signature"
            label="Dugi string borjeva i slova ispod QR-coda"
            type="text"
          />
        </div>
      )}
    </div>
  );
}
