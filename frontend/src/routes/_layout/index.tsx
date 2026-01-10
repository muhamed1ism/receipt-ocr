import { createFileRoute } from "@tanstack/react-router";

import { ReceiptCard } from "@/components/Common/ReceiptCard";
import MonthlyBudget from "@/components/Dashboard/MonthlyBudget";
import WeeklyChart from "@/components/Dashboard/WeeklyChart";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { ChartColumn, CoffeeIcon, TrendingDown } from "lucide-react";
import useAuth from "@/hooks/useAuth";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
});

function Dashboard() {
  const { user: currentUser } = useAuth();
  const progress = 75;

  return (
    <div className="grid grid-cols-4 gap-4">
      <div className="col-span-4">
        <h1 className="text-5xl wrap-normal">
          Pozdrav,
          <span className="ml-2 font-semibold text-primary">
            {/* Muhamed Spahić */}
            {currentUser?.profile?.first_name} {currentUser?.profile?.last_name}
          </span>
        </h1>
      </div>

      <ReceiptCard className="col-span-4">
        <MonthlyBudget
          progress={progress}
          className="rounded-none h-full col-span-1 gap-2 border-y-0"
        />
      </ReceiptCard>

      {/* Amount of receipts this month */}
      <ReceiptCard className="col-span-1">
        <Card className="rounded-none h-full gap-2 border-y-0">
          <CardHeader className="font-semibold text-xl">Broj računa</CardHeader>
          <div className="mx-2 mt-7 border-b-2 border-dashed border-muted-foreground" />

          <CardContent className="font-bold text-2xl text-right">
            23X
          </CardContent>
        </Card>
      </ReceiptCard>

      {/* Average receipts price */}
      <ReceiptCard className="col-span-1">
        <Card className="rounded-none h-full gap-2 border-y-0">
          <CardHeader className="font-semibold text-xl">
            Prosjek po računu
          </CardHeader>
          <div className="mx-2 mt-7 border-b-2 border-dashed border-muted-foreground" />

          <CardContent className="font-bold text-2xl text-right">
            54.20 KM
          </CardContent>
        </Card>
      </ReceiptCard>

      {/* Average receipts price */}
      <ReceiptCard className="col-span-1">
        <Card className="rounded-none h-full gap-2 border-y-0">
          <CardHeader className="font-semibold text-xl">
            Najčešće kupljen proizvod
          </CardHeader>
          <div className="mx-2 border-b-2 border-dashed border-muted-foreground" />

          <CardContent className="font-bold text-2xl text-right">
            Cigare
          </CardContent>
          <CardFooter className="text-muted-foreground text-right">
            <p className="w-full text-right text-xl">60X</p>
          </CardFooter>
        </Card>
      </ReceiptCard>

      {/* Average receipts price */}
      <ReceiptCard className="col-span-1">
        <Card className="rounded-none h-full gap-2 border-y-0">
          <CardHeader className="font-semibold text-xl">
            Najrijeđe kupljen proizvod
          </CardHeader>
          <div className="mx-2 border-b-2 border-dashed border-muted-foreground" />

          <CardContent className="font-bold text-2xl text-right">
            Kondomi
          </CardContent>
          <CardFooter className="text-xl text-muted-foreground">
            <p className="w-full text-right">0X</p>
          </CardFooter>
        </Card>
      </ReceiptCard>

      {/* Average receipts price */}
      <ReceiptCard className="col-span-2">
        <WeeklyChart className="rounded-none h-full gap-2 border-y-0" />
      </ReceiptCard>

      {/* Average receipts price */}
      <ReceiptCard className="col-span-2">
        <Card className="rounded-none h-full gap-2 border-y-0">
          <CardHeader className="font-semibold text-2xl">
            Brzi uvid
            <div className="border-b-2 border-dashed border-muted-foreground" />
          </CardHeader>

          <CardContent className="flex flex-col font-bold text-lg text-right justify-top gap-4 pt-4 h-full">
            <Alert className="inline-flex items-baseline py-4 bg-orange-200/40  dark:bg-orange-300/10 border-orange-400/20">
              <ChartColumn size={8} />
              <AlertDescription className=" text-lg">
                Najviše potrošeno u četvrtak - 200 KM
              </AlertDescription>
            </Alert>

            <Alert className="inline-flex items-baseline py-4 bg-blue-200/40 dark:bg-blue-300/10 border-blue-400/20">
              <CoffeeIcon size={8} />
              <AlertDescription className=" text-lg">
                Ove sedmice ste 5X išli u kafić.
              </AlertDescription>
            </Alert>

            <Alert className="inline-flex items-baseline py-4 bg-green-200/40 dark:bg-green-300/10 border-green-400/20">
              <TrendingDown size={8} />
              <AlertDescription className=" text-lg">
                Najviše potrošeno u četvrtak - 200 KM
              </AlertDescription>
            </Alert>

            <Alert className="inline-flex items-baseline py-4 bg-red-200/40 dark:bg-red-300/10 border-red-400/20">
              <TrendingDown size={8} />
              <AlertDescription className=" text-lg">
                Najviše potrošeno u četvrtak - 200 KM
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </ReceiptCard>
    </div>
  );
}
