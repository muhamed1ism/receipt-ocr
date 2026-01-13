import z from "zod";

const changeEmailFormSchema = z.object({
  email: z.email({ message: "Nevažeća email adresa" }),
});

const changePasswordFormSchema = z
  .object({
    current_password: z
      .string()
      .min(1, { message: "Password is required" })
      .min(8, { message: "Password must be at least 8 characters" }),
    new_password: z
      .string()
      .min(1, { message: "Password is required" })
      .min(8, { message: "Password must be at least 8 characters" }),
    confirm_password: z
      .string()
      .min(1, { message: "Password confirmation is required" }),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "The passwords don't match",
    path: ["confirm_password"],
  });

const updateProfileFormSchema = z.object({
  first_name: z.string().max(30),
  last_name: z.string().max(30),
  phone_number: z.string().max(30).optional(),
  date_of_birth: z.date().optional(),
  country: z.string().max(30).optional(),
  address: z.string().max(30).optional(),
  city: z.string().max(30).optional(),
  currency_preference: z.enum(["USD", "EUR", "BAM", "GBP"]).optional(),
});

export type ChangeEmailFormData = z.infer<typeof changeEmailFormSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordFormSchema>;
export type UpdateProfileFormData = z.infer<typeof updateProfileFormSchema>;

const settingsSchema = {
  changeEmail: changeEmailFormSchema,
  changePassword: changePasswordFormSchema,
  updateProfile: updateProfileFormSchema,
};

export default settingsSchema;
