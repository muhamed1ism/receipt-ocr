import { Appearance } from "@/components/Common/Appearance";
import { Logo } from "@/components/Common/Logo";
import { Footer } from "./Footer";

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="bg-linear-to-t from-emerald-700 to-emerald-500 relative hidden lg:flex lg:items-center lg:justify-center">
        <Logo variant="full" className="h-50" asLink={false} />
      </div>
      <div className="flex flex-col gap-4 bg-yellow-100/20 dark:bg-yellow-50/10 p-6 md:p-10 tracking-wide">
        <div className="flex justify-end">
          <Appearance />
        </div>
        <div className="flex flex-1 items-center justify-center border-t-2 border-dashed border-foreground">
          <div className="w-full max-w-xs receipt-text">{children}</div>
        </div>
        <Footer />
      </div>
    </div>
  );
}
