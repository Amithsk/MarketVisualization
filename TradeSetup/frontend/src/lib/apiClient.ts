//frontend/src/lib/apiClient.ts
import axios, { AxiosError, AxiosInstance } from "axios";
import type { ApiError } from "@/types/common.types";

/**
 * Shared Axios client for frontend → backend communication.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Response interceptor
 *
 * IMPORTANT:
 * - Never replace the thrown error
 * - Always throw a real Error / AxiosError
 * - Attach normalized data instead of discarding context
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const normalizedError: ApiError = {
      status: error.response?.status ?? 500,
      message:
        (error.response?.data as any)?.message ||
        (error.response?.data as any)?.detail ||
        error.message ||
        "Unexpected API error",
      raw: error.response?.data,
    };

    // 🔒 Preserve the original AxiosError
    (error as any).normalized = normalizedError;

    // Optional but very useful for debugging
    console.error("[API][AXIOS][ERROR]", {
      url: error.config?.url,
      method: error.config?.method,
      status: normalizedError.status,
      message: normalizedError.message,
    });

    return Promise.reject(error);
  }
);

export default apiClient;
