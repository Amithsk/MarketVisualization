// src/lib/apiClient.ts

import axios, { AxiosError, AxiosInstance } from "axios";

/**
 * Shared Axios client for frontend → backend communication.
 * All API calls must go through this instance.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Normalized API error shape
 */
export interface ApiError {
  status: number;
  message: string;
  raw?: any;
}

/**
 * Response interceptor
 * Normalizes backend + network errors into a predictable shape
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