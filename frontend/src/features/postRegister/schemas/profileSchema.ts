import z from "zod";

export const addProfileMeFormSchema = z.object({
  first_name: z.string(),
  last_name: z.string(),
  phone_number: z.string().optional(),
  date_of_birth: z.string().optional(),
  country: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
});

export type AddProfileMeFormData = z.infer<typeof addProfileMeFormSchema>;

const profileSchema = {
  addProfileMe: addProfileMeFormSchema,
};

export default profileSchema;
