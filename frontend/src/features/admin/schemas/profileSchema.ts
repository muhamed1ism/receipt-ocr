import z from "zod";

export const addProfileFormSchema = z.object({
  first_name: z.string(),
  last_name: z.string(),
  phone_number: z.string().optional(),
  date_of_birth: z.string().optional(),
  country: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
});

const editProfileFormSchema = z.object({
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  phone_number: z.string().optional(),
  date_of_birth: z.string().optional(),
  country: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
});

export type AddProfileFormData = z.infer<typeof addProfileFormSchema>;
export type EditProfileFormData = z.infer<typeof editProfileFormSchema>;

const profileSchema = {
  addProfile: addProfileFormSchema,
  editProfile: editProfileFormSchema,
};

export default profileSchema;
