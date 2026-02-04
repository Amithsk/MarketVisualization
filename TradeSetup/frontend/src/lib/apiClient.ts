// src/lib/apiClient.ts

import axios, { AxiosError, AxiosInstance } from "axios";

/**
 * Shared Axios client for frontend → backend communication.
 * All API calls must go through this instance.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: "", // same-origin (/api/*)
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Basic response interceptor.
 * Keeps UI and services clean.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Normalize error shape
    const normalizedError = {
      status: error.response?.status,
      message:
        (error.response?.data as any)?.message ||
        error.message ||
        "Unexpected API error",
    };

    return Promise.reject(normalizedError);
  }
);

export default apiClient;