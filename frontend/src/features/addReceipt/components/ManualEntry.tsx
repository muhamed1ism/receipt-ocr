import { ReceiptCard } from "@/components/Common/ReceiptCard";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronDown, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import z from "zod";

const receiptFormSchema = z.object({
  store: z.object({
    name: z.string().min(1, "Naziv prodavnice je obavezan"),
    jib: z.string().optional(),
    pib: z.string().optional(),
  }),
  branch: z.object({
    address: z.string().optional(),
    city: z.string().optional(),
    store_id: z.string(),
  }),
  details: z.object({
    ibfm: z.string().optional(),
    bf: z.number().optional(),
    ibk: z.number().optional(),
    digital_signature: z.string().optional(),
  }),
  date_time: z.string(),
  payment_method: z.string().optional(),
  currency: z.enum(["BAM", "EUR", "USD", "GBP"]),
  tax_amount: z.number().optional(),
  total_amount: z.number().optional(),
  items: z
    .array(
      z.object({
        name: z.string().min(1, "Naziv artikla je obavezan"),
        quantity: z.number().min(0.001),
        price: z.number().min(0),
        total_price: z.number().min(0),
      }),
    )
    .min(1, "Morate dodati barem jedan artikal"),
});

type ReceiptFormValues = z.infer<typeof receiptFormSchema>;

export function ManualEntry() {
  const [expandedDetails, setExpandedDetails] = useState(false);

  const form = useForm<ReceiptFormValues>({
    resolver: zodResolver(receiptFormSchema),
    defaultValues: {
      store: { name: "", jib: "", pib: "" },
      branch: { address: "", city: "" },
      details: {
        ibfm: "",
        bf: undefined,
        ibk: undefined,
        digital_signature: "",
      },
      date_time: new Date().toISOString().slice(0, 16),
      payment_method: "",
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
    const total = items.reduce((sum, item) => sum + (item.total_price || 0), 0);
    form.setValue("total_amount", total);
  };

  const onSubmit = (data: ReceiptFormValues) => {
    console.log("Form submitted:", data);
  };

  return (
    <div className="font-receipt max-w-2xl mx-auto">
      <ReceiptCard className="p-6 lg:p-8">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Store Info Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Podaci o prodavnici</h2>
              <FormField
                control={form.control}
                name="store.name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Naziv prodavnice *</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Unesite naziv prodavnice"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="store.jib"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>JIB</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Jedinstveni identifikacijski broj"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="store.pib"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>PIB</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Poreski identifikacijski broj"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="border-b-2 border-dashed border-muted-foreground" />

            {/* Branch Info Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Podaci o filijali</h2>
              <FormField
                control={form.control}
                name="branch.address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Adresa</FormLabel>
                    <FormControl>
                      <Input placeholder="Unesite adresu" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="branch.city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Grad</FormLabel>
                    <FormControl>
                      <Input placeholder="Unesite grad" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="border-b-2 border-dashed border-muted-foreground" />

            {/* Receipt Details Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Detalji računa</h2>
              <FormField
                control={form.control}
                name="date_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Datum i vrijeme *</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="payment_method"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Način plaćanja</FormLabel>
                    <FormControl>
                      <Input placeholder="Npr. Gotovina, Kartica" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valuta *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="BAM">BAM</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="GBP">GBP</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="border-b-2 border-dashed border-muted-foreground" />

            {/* Technical Details Section (Collapsible) */}
            <div className="space-y-4">
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
                <div className="space-y-4 pl-4">
                  <FormField
                    control={form.control}
                    name="details.ibfm"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>IBFM</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="details.bf"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>BF</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            name={field.name}
                            ref={field.ref}
                            onBlur={field.onBlur}
                            value={field.value ?? ""}
                            onChange={(e) =>
                              field.onChange(
                                e.target.value
                                  ? parseFloat(e.target.value)
                                  : undefined,
                              )
                            }
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="details.ibk"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>IBK</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            name={field.name}
                            ref={field.ref}
                            onBlur={field.onBlur}
                            value={field.value ?? ""}
                            onChange={(e) =>
                              field.onChange(
                                e.target.value
                                  ? parseFloat(e.target.value)
                                  : undefined,
                              )
                            }
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="details.digital_signature"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Digitalni potpis</FormLabel>
                        <FormControl>
                          <Input {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              )}
            </div>

            <div className="border-b-2 border-dashed border-muted-foreground" />

            {/* Items Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Artikli</h2>
              <div className="space-y-3">
                {fields.map((field, index) => (
                  <div key={field.id} className="space-y-2 p-4 border rounded">
                    <FormField
                      control={form.control}
                      name={`items.${index}.name`}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Naziv *</FormLabel>
                          <FormControl>
                            <Input placeholder="Naziv artikla" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <div className="grid grid-cols-3 gap-3">
                      <FormField
                        control={form.control}
                        name={`items.${index}.quantity`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Količina</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                step="0.001"
                                name={field.name}
                                ref={field.ref}
                                onBlur={field.onBlur}
                                value={field.value}
                                onChange={(e) => {
                                  const quantity =
                                    parseFloat(e.target.value) || 1;
                                  field.onChange(quantity);
                                  const price =
                                    form.getValues(`items.${index}.price`) || 0;
                                  form.setValue(
                                    `items.${index}.total_price`,
                                    price * quantity,
                                  );
                                  calculateTotal();
                                }}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name={`items.${index}.price`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Cijena *</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                step="0.01"
                                name={field.name}
                                ref={field.ref}
                                onBlur={field.onBlur}
                                value={field.value}
                                onChange={(e) => {
                                  const price = parseFloat(e.target.value) || 0;
                                  field.onChange(price);
                                  const quantity =
                                    form.getValues(`items.${index}.quantity`) ||
                                    1;
                                  form.setValue(
                                    `items.${index}.total_price`,
                                    price * quantity,
                                  );
                                  calculateTotal();
                                }}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name={`items.${index}.total_price`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Ukupno</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                step="0.01"
                                disabled
                                name={field.name}
                                ref={field.ref}
                                onBlur={field.onBlur}
                                value={field.value}
                                onChange={() => {}}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
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

            <div className="border-b-2 border-dashed border-muted-foreground" />

            {/* Totals Section */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Ukupno</h2>
              <FormField
                control={form.control}
                name="tax_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Porez</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        name={field.name}
                        ref={field.ref}
                        onBlur={field.onBlur}
                        value={field.value ?? ""}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value
                              ? parseFloat(e.target.value)
                              : undefined,
                          )
                        }
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="total_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Ukupan iznos</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        disabled
                        name={field.name}
                        ref={field.ref}
                        onBlur={field.onBlur}
                        value={field.value ?? 0}
                        onChange={() => {}}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button type="submit" className="w-full">
              Spremi račun
            </Button>
          </form>
        </Form>
      </ReceiptCard>
    </div>
  );
}
