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

    return Promise.reject(normalizedError);
  }
);

export default apiClient;
