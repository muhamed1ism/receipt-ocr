import { Bar, BarChart, LabelList, XAxis } from "recharts";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";

interface WeeklyChartType {
  className?: string;
}

export default function WeeklyChart({ className }: WeeklyChartType) {
  const chartData = [
    { day: "Ponedjeljak", spending: 186 },
    { day: "Utorak", spending: 305 },
    { day: "Srijeda", spending: 237 },
    { day: "Četvrtak", spending: 73 },
    { day: "Petak", spending: 209 },
    { day: "Subota", spending: 214 },
    { day: "Nedjelja", spending: 214 },
  ];

  const chartConfig = {
    spending: {
      label: "Potrošnja",
    },
  } satisfies ChartConfig;

  return (
    <Card className={className}>
      <CardHeader>
        <h4 className="font-semibold text-2xl">Troškovi ove sedmice</h4>
        <div className="border-b-2 border-dashed border-muted-foreground" />
      </CardHeader>
      <CardContent className="h-full flex items-center">
        <ChartContainer config={chartConfig} className="w-full">
          <BarChart accessibilityLayer data={chartData}>
            <Bar dataKey="spending" fill="var(--primary)" radius={16}>
              <LabelList
                dataKey="spending"
                position="top"
                className="font-semibold fill-primary font-sans"
                fontSize={12}
                formatter={(value: number) => `${value} KM`}
              />
            </Bar>
            <XAxis
              className="font-sans"
              dataKey="day"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
