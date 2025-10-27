import { useState, useEffect, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiRequestOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: AxiosError) => void;
  immediate?: boolean;
}

/**
 * Custom hook for API requests with loading, error states, and cancellation
 */
export function useApiRequest<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiRequestOptions<T> = {}
) {
  const { onSuccess, onError, immediate = false } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosError | null>(null);

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiFunction(...args);
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        const axiosError = err as AxiosError;
        setError(axiosError);
        onError?.(axiosError);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, onSuccess, onError]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, execute, reset };
}
