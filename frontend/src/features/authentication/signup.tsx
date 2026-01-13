import { zodResolver } from "@hookform/resolvers/zod";
import { Link as RouterLink } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { AuthLayout } from "@/components/Common/AuthLayout";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { LoadingButton } from "@/components/ui/loading-button";
import { PasswordInput } from "@/components/ui/password-input";
import useAuth from "@/hooks/useAuth";
import authSchema, { SignUpFormData } from "./schemas/authSchema";

export default function SignUp() {
  const { signUpMutation } = useAuth();
  const form = useForm<SignUpFormData>({
    resolver: zodResolver(authSchema.signUp),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      password: "",
      confirm_password: "",
    },
  });

  const onSubmit = (data: SignUpFormData) => {
    if (signUpMutation.isPending) return;

    // exclude confirm_password from submission data
    const { confirm_password: _confirm_password, ...submitData } = data;
    signUpMutation.mutate(submitData);
  };

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Kreirajte račun</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="user@example.com"
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Lozinka</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Lozinka"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirm_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Potvrdi lozinku</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="confirm-password-input"
                      placeholder="Potvrdi lozinku"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              loading={signUpMutation.isPending}
              className="w-full mt-2 font-semibold"
            >
              Registrujte se
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Već imate račun? <br />
            <RouterLink
              to="/login"
              className="underline underline-offset-4 font-bold"
            >
              Prijavi se
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
}
