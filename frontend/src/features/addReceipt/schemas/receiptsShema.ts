import z from "zod";

const addReceiptFormSchema = z.object({
  store: z.object({
    name: z.string().min(2, "Naziv prodavnice je obavezan"),
    jib: z.string().optional(),
    pib: z.string().optional(),
  }),
  branch: z.object({
    address: z.string().min(2, "Adresa je obavezana"),
    city: z.string().min(2, "Naziv grada je obavezan"),
  }),
  details: z.object({
    ibfm: z.string().optional(),
    // bf: z.number().or(string()).optional(),
    bf: z.number().optional(),
    digital_signature: z.string().optional(),
  }),
  // date_time: z.date({ error: "Pogrešan datum" }),
  date_time: z.string(),
  payment_method: z.string().optional(),
  currency: z.enum(["BAM", "EUR", "USD", "GBP"]),
  tax_amount: z.number().optional(),
  total_amount: z.number().optional(),
  items: z
    .array(
      z.object({
        name: z.string().min(1, "Naziv artikla je obavezan"),
        quantity: z
          .number({ error: "Vrijednost mora biti veća od 0" })
          .min(0)
          .max(99999),
        // price: z
        //   .number({ error: "Cijena artikla je obavezna" })
        //   .min(0.01)
        //   .or(
        //     string().refine((val) => Number(val) !== 0, {
        //       message: "Vrijednost mora biti veća od 0",
        //     }),
        //   ),
        price: z.number({ error: "Cijena artikla je obavezna" }),
        total_price: z.number(),
      }),
    )
    .min(1, "Morate dodati barem jedan artikal"),
});

export type AddReceiptFormData = z.infer<typeof addReceiptFormSchema>;

const receiptsShema = {
  addReceipt: addReceiptFormSchema,
};

export default receiptsShema;
