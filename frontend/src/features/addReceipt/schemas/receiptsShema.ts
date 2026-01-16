import z from "zod";

const addReceiptFormSchema = z.object({
  store: z.object({
    name: z.string().min(1, "Naziv prodavnice je obavezan"),
    jib: z.string().optional(),
    pib: z.string().optional(),
  }),
  branch: z.object({
    address: z.string().optional(),
    city: z.string().optional(),
  }),
  details: z.object({
    ibfm: z.string().optional(),
    bf: z.string().optional(),
    ibk: z.string().optional(),
    digital_signature: z.string().optional(),
  }),
  date_time: z.string(),
  payment_method: z.string().optional(),
  currency: z.enum(["BAM", "EUR", "USD", "GBP"]),
  tax_amount: z.coerce.number().optional(),
  total_amount: z.coerce.number().optional(),
  items: z
    .array(
      z.object({
        name: z.string().min(1, "Naziv artikla je obavezan"),
        quantity: z.coerce.number().min(0.001).max(99999),
        price: z.coerce.number().min(0.01).max(99999),
        total_price: z.coerce.number().min(0.01).max(99999)
      })
    )
    .min(1, "Morate dodati barem jedan artikal"),
});

export type AddReceiptFormValues = z.infer<typeof addReceiptFormSchema>;

const receiptsShema = {
  addReceipt: addReceiptFormSchema,
};

export default receiptsShema;
