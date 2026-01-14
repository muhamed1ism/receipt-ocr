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
import authSchema, { LoginFormData } from "./schemas/authSchema";

export default function Login() {
  const { loginMutation } = useAuth();
  const form = useForm<LoginFormData>({
    resolver: zodResolver(authSchema.login),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = (data: LoginFormData) => {
    if (loginMutation.isPending) return;
    loginMutation.mutate(data);
  };

  return (
    <AuthLayout>
      <h1 className="block lg:hidden uppercase text-4xl font-medium text-center mt-4 mb-20">
        Troškomjer
      </h1>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Prijavi se na svoj račun</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      className=""
                      data-testid="email-input"
                      placeholder="user@example.com"
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center">
                    <FormLabel>Lozinka</FormLabel>
                  </div>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                  <RouterLink
                    to="/recover-password"
                    className="ml-auto text-sm underline-offset-4 hover:underline mt-2"
                  >
                    Zaboravili ste lozinku?
                  </RouterLink>
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              className="w-full font-semibold"
              loading={loginMutation.isPending}
            >
              Prijavi se
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Još nemate račun? <br />
            <RouterLink
              to="/signup"
              className="underline underline-offset-4 font-semibold"
            >
              Registrujte se
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  );
}
