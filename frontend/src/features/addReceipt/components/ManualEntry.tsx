import DynamicFormField from "@/components/Forms/DynamicFormField";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { currencyPreference } from "@/constants/currency-preference";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronDown, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import receiptsShema, { AddReceiptFormValues } from "../schemas/receiptsShema";
import useAddReceipt from "../hooks/useAddReceipt";
import { paymentMethod } from "@/constants/payment-method";

export function ManualEntry() {
  const [expandedDetails, setExpandedDetails] = useState(false);
  const mutation = useAddReceipt();

  const form = useForm<AddReceiptFormValues>({
    resolver: zodResolver(receiptsShema.addReceipt),
    defaultValues: {
      store: { name: "", jib: "", pib: "" },
      branch: { address: "", city: "" },
      details: {
        ibfm: "",
        bf: "",
        ibk: "",
        digital_signature: "",
      },
      date_time: new Date().toISOString().slice(0, 16),
      payment_method: "Gotovina",
      currency: "BAM",
      tax_amount: undefined,
      total_amount: 0,
      items: [{ name: "", quantity: 1, price: 0, total_price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "items",
  });

  const calculateTotal = () => {
    const items = form.getValues("items");
    const total =
      Math.round(
        items.reduce((sum, item) => sum + (item.total_price || 0), 0) * 100
      ) / 100;
    const pdv = Math.round((total - total / 1.17) * 100) / 100; // 17% PDV

    form.setValue("total_amount", total);
    form.setValue("tax_amount", pdv);
  };

  const onSubmit = (data: AddReceiptFormValues) => {
    mutation.mutate(data);
  };

  return (
    <div className="font-receipt max-w-2xl mx-auto space-y-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Store Info Section */}

          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Podaci o prodavnici</h2>
            <div className="grid grid-cols-2 gap-8">
              <DynamicFormField
                label="Naziv prodavnice"
                control={form.control}
                name="store.name"
                type="text"
              />
              <DynamicFormField
                label="Grad"
                control={form.control}
                name="branch.city"
                type="text"
              />
              <DynamicFormField
                label="Adresa"
                control={form.control}
                name="branch.address"
                type="text"
              />
              <DynamicFormField
                control={form.control}
                name="date_time"
                label="Datum"
                type="date"
              />
            </div>
            {/* Technical Details Section (Collapsible) */}
            {/* ne zaboravit izbacit detalje ako zelis testirat pravljenje racuna */}
            <div className="space-y-4 mt-2">
              <button
                type="button"
                onClick={() => setExpandedDetails(!expandedDetails)}
                className="flex items-center gap-2 text-sm font-semibold hover:text-muted-foreground"
              >
                <ChevronDown
                  size={18}
                  className={`transition-transform ${expandedDetails ? "rotate-180" : ""}`}
                />
                Tehnički detalji
              </button>
              {expandedDetails && (
                <div className="space-y-4">
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
                    type="text"
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
          </div>

          <div className="border-b-2 border-dashed border-muted-foreground" />

          {/* Receipt Details Section */}
          <div className="grid grid-cols-2">
            <DynamicFormField
              control={form.control}
              name="payment_method"
              label="način plaćanja"
              type="select"
              options={paymentMethod}
            />

            <DynamicFormField
              label="Valuta"
              control={form.control}
              name="currency"
              type="select"
              options={currencyPreference}
            />
          </div>

          <div className="border-b-2 border-dashed border-muted-foreground" />

          {/* Items Section */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Artikli</h2>

            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="space-y-2 p-4 border rounded">
                  <DynamicFormField
                    control={form.control}
                    label="Artikal"
                    name={`items.${index}.name`}
                    type="text"
                  />
                  <div className="grid grid-cols-3 gap-3">
                    <DynamicFormField
                      control={form.control}
                      label="Količina"
                      name={`items.${index}.quantity`}
                      type="number"
                      onChange={(quantity) => {
                        const price =
                          form.getValues(`items.${index}.price`) || 0;
                        form.setValue(
                          `items.${index}.total_price`,
                          Math.round(price * quantity * 100) / 100
                        );
                        calculateTotal();
                      }}
                    />
                    <DynamicFormField
                      control={form.control}
                      label="Cijena"
                      name={`items.${index}.price`}
                      type="number"
                      onChange={(price) => {
                        const quantity =
                          form.getValues(`items.${index}.quantity`) || 1;
                        form.setValue(
                          `items.${index}.total_price`,
                          Math.round(price * quantity * 100) / 100
                        );
                        calculateTotal();
                      }}
                    />
                    <DynamicFormField
                      control={form.control}
                      label="Ukupno"
                      name={`items.${index}.total_price`}
                      type="number"
                      disabled
                    />
                  </div>
                  {fields.length > 1 && (
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onClick={() => {
                        remove(index);
                        calculateTotal();
                      }}
                      className="mt-2"
                    >
                      <Trash2 size={16} className="mr-2" />
                      Ukloni
                    </Button>
                  )}
                </div>
              ))}
            </div>
            <Button
              type="button"
              variant="outline"
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
          </div>

          {/* Totals Section - outside ReceiptCard */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Ukupno</h2>
            <DynamicFormField
              control={form.control}
              name="tax_amount"
              label="Porez"
              type="number"
              disabled
            />
            <DynamicFormField
              control={form.control}
              name="total_amount"
              label="Ukupan iznos"
              type="number"
              disabled
            />
          </div>

          <Button type="submit" className="w-full">
            Spremi račun
          </Button>
        </form>
      </Form>
    </div>
  );
}
