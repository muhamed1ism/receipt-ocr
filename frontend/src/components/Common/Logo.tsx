import { Link } from "@tanstack/react-router"

import { useTheme } from "@/components/theme-provider"
import { cn } from "@/lib/utils"
import icon from "/assets/images/icon.svg"
import iconLight from "/assets/images/icon-light.svg"
import logo from "/assets/images/logo.svg"
import logoHorizontal from "/assets/images/logo-horizontal.svg"
import logoHorizontalLight from "/assets/images/logo-horizontal-light.svg"
import logoLight from "/assets/images/logo-light.svg"

interface LogoProps {
  variant?:
    | "full"
    | "full-light"
    | "icon"
    | "responsive"
    | "horizontal-responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  const fullLogo = isDark ? logoLight : logo
  const iconLogo = isDark ? iconLight : icon
  const horizontalLogo = isDark ? logoHorizontalLight : logoHorizontal

  const content =
    variant === "responsive" ? (
      <>
        <img
          src={fullLogo}
          alt="FastAPI"
          className={cn(
            "h-6 w-auto group-data-[collapsible=icon]:hidden",
            className,
          )}
        />
        <img
          src={iconLogo}
          alt="FastAPI"
          className={cn(
            "size-5 hidden group-data-[collapsible=icon]:block",
            className,
          )}
        />
      </>
    ) : variant === "horizontal-responsive" ? (
      <>
        <img
          src={horizontalLogo}
          alt="FastAPI"
          className={cn(
            "h-8 w-full group-data-[collapsible=icon]:hidden",
            className,
          )}
        />
        <img
          src={iconLogo}
          alt="FastAPI"
          className={cn(
            "size-6 hidden group-data-[collapsible=icon]:block",
            className,
          )}
        />
      </>
    ) : (
      <img
        src={
          variant === "full"
            ? fullLogo
            : variant === "full-light"
              ? logoLight
              : iconLogo
        }
        alt="FastAPI"
        className={cn(
          variant === "full" || variant === "full-light"
            ? "h-6 w-auto"
            : "size-5",
          className,
        )}
      />
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
