import { Skeleton } from "@/components/ui/skeleton";

const PendingSettingsProfile = () => (
  <div className="grid grid-cols-2 gap-8">
    {[...Array(4)].map((_, index) => (
      <div key={index}>
        <Skeleton className="h-4" />
        <Skeleton className="h-5" />
      </div>
    ))}
    {[...Array(4)].map((_, index) => (
      <div key={index}>
        <Skeleton className="h-4" />
        <Skeleton className="h-5" />
      </div>
    ))}
  </div>
);

export default PendingSettingsProfile;
