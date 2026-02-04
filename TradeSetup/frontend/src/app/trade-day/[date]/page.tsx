// frontend/src/app/trade-day/[date]/page.tsx

import TradeDayClient from "./TradeDayClient";
import type { TradeDate } from "@/types/common.types";

interface TradeDayPageProps {
  params: Promise<{
    date: TradeDate;
  }>;
}

export default async function TradeDayPage({
  params,
}: TradeDayPageProps) {
  const { date } = await params;

  return <TradeDayClient tradeDate={date} />;
}