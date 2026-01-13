import { UsersService } from "@/client";

interface useGetUsersProps {
  query: string;
  skip?: number;
  limit?: number;
}

const useGetUsers = ({ query, skip = 0, limit = 30 }: useGetUsersProps) => {
  return {
    queryKey: ["users", query],
    queryFn: () =>
      UsersService.readUsers({
        skip,
        limit,
        q: query || undefined,
      }),
  };
};

export default useGetUsers;
