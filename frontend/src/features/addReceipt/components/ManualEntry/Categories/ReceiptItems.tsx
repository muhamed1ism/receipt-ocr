import DynamicFormField from "@/components/Forms/DynamicFormField";
import { Button } from "@/components/ui/button";
import { currencyPreference } from "@/constants/currency-preference";
import { AddReceiptFormData } from "@/features/addReceipt/schemas/receiptsShema";
import { ChevronRight, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useFieldArray, UseFormReturn } from "react-hook-form";

interface ReceiptItemsProps {
  form: UseFormReturn<AddReceiptFormData>;
}

export default function ReceiptItems({ form }: ReceiptItemsProps) {
  const currencyValue = form.watch("currency"); // reactive
  const currency =
    currencyPreference.find((c) => c.value === currencyValue) ||
    currencyPreference[0];

  const [expanded, setExpanded] = useState(true);

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "items",
  });

  const calculateTotal = () => {
    const items = form.getValues("items");
    const total =
      Math.round(
        items.reduce((sum, item) => sum + (item.total_price || 0), 0) * 100,
      ) / 100;
    const pdv = Math.round((total - total / 1.17) * 100) / 100; // 17% PDV

    form.setValue("total_amount", total);
    form.setValue("tax_amount", pdv);
  };

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
        Artikli
      </button>

      {expanded && (
        <>
          {fields.map((field, index) => (
            <div
              key={field.id}
              className="flex bg-accent shadow-inner shadow-black/10 flex-col lg:flex-row w-full gap-4 p-4 border dark:border-zinc-950/60 dark:shadow-black/40 rounded"
            >
              <div className="flex gap-4 w-full lg:w-7/8">
                <DynamicFormField
                  control={form.control}
                  label="Artikal"
                  name={`items.${index}.name`}
                  type="text"
                />

                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="destructive"
                    size="icon"
                    onClick={() => {
                      remove(index);
                      calculateTotal();
                    }}
                    className="lg:hidden self-end"
                  >
                    <Trash2 size={16} />
                  </Button>
                )}
              </div>

              <div className="flex flex-row gap-4">
                <div className="w-3/11">
                  <DynamicFormField
                    control={form.control}
                    label="Količina"
                    name={`items.${index}.quantity`}
                    type="decimal"
                    onChange={(quantity) => {
                      const price = form.getValues(`items.${index}.price`) || 0;
                      form.setValue(
                        `items.${index}.total_price`,
                        Math.round(Number(price) * (quantity || 0) * 100) / 100,
                      );
                      calculateTotal();
                    }}
                  />
                </div>

                <div className="w-4/11">
                  <DynamicFormField
                    control={form.control}
                    label="Cijena"
                    name={`items.${index}.price`}
                    type="decimal"
                    append={
                      currency.position === "append"
                        ? currency.symbol
                        : undefined
                    }
                    prepend={
                      currency.position === "prepend"
                        ? currency.symbol
                        : undefined
                    }
                    onChange={(price) => {
                      const quantity =
                        form.getValues(`items.${index}.quantity`) || 1;
                      form.setValue(
                        `items.${index}.total_price`,
                        Math.round((price || 0) * quantity * 100) / 100,
                      );
                      calculateTotal();
                    }}
                  />
                </div>

                <div className="w-4/11 lg:mr-4">
                  <DynamicFormField
                    control={form.control}
                    label="Ukupno"
                    name={`items.${index}.total_price`}
                    type="decimal"
                    append={
                      currency.position === "append"
                        ? currency.symbol
                        : undefined
                    }
                    prepend={
                      currency.position === "prepend"
                        ? currency.symbol
                        : undefined
                    }
                    disabled
                  />
                </div>

                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="default"
                    size="lg"
                    onClick={() => {
                      remove(index);
                      calculateTotal();
                    }}
                    className="bg-destructive hover:bg-destructive/70 hidden lg:block self-end"
                  >
                    <Trash2 size={16} />
                  </Button>
                )}
              </div>
            </div>
          ))}

          <Button
            type="button"
            variant="default"
            onClick={() => {
              append({
                name: "",
                quantity: 1,
                price: 0,
                total_price: 0,
              });
            }}
            className="w-full"
          >
            <Plus size={16} className="mr-2" />
            Dodaj artikal
          </Button>
        </>
      )}
    </div>
  );
}
