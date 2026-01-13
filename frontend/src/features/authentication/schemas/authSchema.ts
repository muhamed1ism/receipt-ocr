import z from "zod";
import type { Body_login_login_access_token as AccessToken } from "@/client";

const signUpFormSchema = z
  .object({
    email: z.email(),
    password: z
      .string()
      .min(1, { message: "Lozinka je obavezna" })
      .min(8, { message: "Lozinka mora imati najmanje 8 karaktera" }),
    confirm_password: z
      .string()
      .min(1, { message: "Potvrda lozinke je obavezna" }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Lozinke se ne podudaraju",
    path: ["confirm_password"],
  });

const loginFormSchema = z.object({
  username: z.email(),
  password: z
    .string()
    .min(1, { message: "Lozinka je obavezna" })
    .min(8, { message: "Lozinka mora imati najmanje 8 karaktera" }),
}) satisfies z.ZodType<AccessToken>;

const recoverPasswordFormSchema = z.object({
  email: z.email(),
});

const resetPasswordFormSchema = z
  .object({
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

export type SignUpFormData = z.infer<typeof signUpFormSchema>;
export type LoginFormData = z.infer<typeof loginFormSchema>;
export type RecoverPasswordFormData = z.infer<typeof recoverPasswordFormSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordFormSchema>;

const authSchema = {
  signUp: signUpFormSchema,
  login: loginFormSchema,
  recoverPassword: recoverPasswordFormSchema,
  resetPassword: resetPasswordFormSchema,
};

export default authSchema;
