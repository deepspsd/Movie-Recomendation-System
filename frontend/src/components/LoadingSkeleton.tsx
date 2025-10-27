import { Skeleton } from '@/components/ui/skeleton';

export const MovieCardSkeleton = () => {
  return (
    <div className="space-y-3">
      <Skeleton className="aspect-[2/3] w-full rounded-xl" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  );
};

export const MovieDetailsSkeleton = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Skeleton */}
      <div className="relative h-[80vh]">
        <Skeleton className="absolute inset-0" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
        <div className="relative z-10 h-full flex items-center">
          <div className="container mx-auto px-4">
            <div className="flex gap-8">
              <Skeleton className="w-80 h-[480px] rounded-xl" />
              <div className="flex-1 space-y-4">
                <Skeleton className="h-12 w-2/3" />
                <Skeleton className="h-6 w-1/3" />
                <Skeleton className="h-24 w-full" />
                <div className="flex gap-4">
                  <Skeleton className="h-12 w-32" />
                  <Skeleton className="h-12 w-32" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Movies Skeleton */}
      <div className="container mx-auto px-4 py-16">
        <Skeleton className="h-8 w-48 mb-8" />
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {[...Array(6)].map((_, i) => (
            <MovieCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
};

export const DashboardSkeleton = () => {
  return (
    <div className="min-h-screen bg-background pt-16">
      {/* Hero Skeleton */}
      <div className="relative h-[80vh]">
        <Skeleton className="absolute inset-0" />
      </div>

      {/* Sections Skeleton */}
      <div className="container mx-auto px-4 space-y-16 py-16">
        {[...Array(3)].map((_, sectionIndex) => (
          <div key={sectionIndex}>
            <Skeleton className="h-8 w-64 mb-8" />
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {[...Array(5)].map((_, i) => (
                <MovieCardSkeleton key={i} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const SearchSkeleton = () => {
  return (
    <div className="min-h-screen bg-background pt-24">
      <div className="container mx-auto px-4">
        <Skeleton className="h-12 w-full max-w-2xl mx-auto mb-12" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {[...Array(20)].map((_, i) => (
            <MovieCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
};
