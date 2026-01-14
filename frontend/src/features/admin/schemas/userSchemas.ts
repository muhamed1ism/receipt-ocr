import z from "zod";

const addUserFormSchema = z
  .object({
    email: z.email({ message: "Neispravna email adresa" }),
    password: z
      .string()
      .min(1, { message: "Lozinka je obavezna" })
      .min(8, { message: "Lozinka mora imati najmanje 8 karaktera" }),
    confirm_password: z
      .string()
      .min(1, { message: "Molimo potvrdite svoju lozinku" }),
    is_superuser: z.boolean(),
    is_active: z.boolean(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Lozinke se ne podudaraju",
    path: ["confirm_password"],
  });

const editUserFormSchema = z
  .object({
    email: z.email({ message: "Neispravna email adresa" }),
    password: z
      .string()
      .min(8, { message: "Lozinka mora imati najmanje 8 karaktera" })
      .optional()
      .or(z.literal("")),
    confirm_password: z.string().optional(),
    is_superuser: z.boolean().optional(),
    is_active: z.boolean().optional(),
  })
  .refine((data) => !data.password || data.password === data.confirm_password, {
    message: "Lozinke se ne podudaraju",
    path: ["confirm_password"],
  });

export type AddUserFormData = z.infer<typeof addUserFormSchema>;
export type EditUserFormData = z.infer<typeof editUserFormSchema>;

const userSchema = {
  addUser: addUserFormSchema,
  editUser: editUserFormSchema,
};

export default userSchema;
