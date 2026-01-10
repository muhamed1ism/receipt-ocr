export function formatDate(datetime: string | Date): string {
  const date = typeof datetime === "string" ? new Date(datetime) : datetime;

  return new Intl.DateTimeFormat("hr-HR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

export function formatTime(datetime: string | Date): string {
  const date = typeof datetime === "string" ? new Date(datetime) : datetime;

  return new Intl.DateTimeFormat("hr-HR", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}
