import axios from "axios";

type ApiErrorBody = {
  detail?: string | { msg?: string }[];
};

export function getErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return error instanceof Error ? error.message : fallback;
  }

  const detail = error.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail[0]?.msg) {
    return detail[0].msg;
  }
  return fallback;
}

