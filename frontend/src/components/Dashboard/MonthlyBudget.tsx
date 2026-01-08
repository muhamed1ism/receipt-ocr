import { Card, CardHeader, CardContent } from "../ui/card";
import { Progress } from "../ui/progress";

interface MonthlyBudgetType {
  progress: number;
  className?: string;
}

export default function MonthlyBudget({
  progress,
  className,
}: MonthlyBudgetType) {
  const adjustedProgress =
    progress < 100 ? (progress === 0 ? 0 : progress - 1) : progress - 4;

  return (
    <Card className={className}>
      <CardHeader className="inline-flex items-baseline justify-between">
        <h6 className="font-semibold text-xl">Mjesečni budžet</h6>
        <h6>Preostalo dana</h6>
      </CardHeader>

      <CardContent>
        <div className="flex justify-between items-baseline pb-4">
          <div className="inline-flex items-baseline gap-4">
            <h4 className="text-3xl font-bold text-primary">1247.50 KM</h4>
            <p className="text-lg text-muted-foreground">od 2000KM</p>
          </div>

          <div>
            <h4 className="text-end text-2xl font-semibold">24</h4>
          </div>
        </div>

        <Progress value={progress} />
        <p
          className="text-primary pt-2 font-sans"
          style={{ paddingLeft: `${adjustedProgress}%` }}
        >
          {progress} %
        </p>
      </CardContent>
    </Card>
  );
}
