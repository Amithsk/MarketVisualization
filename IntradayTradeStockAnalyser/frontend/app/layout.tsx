/*IntradayTradeStockAnalyser/frontend/app/layout.tsx*/
/* IntradayTradeStockAnalyser/frontend/app/layout.tsx */

import "./globals.css";
import Link from "next/link";

export const metadata = {
    title: "Intraday Replay System",
    description: "Context-aware replay platform",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>

                {/* ========================================= */}
                {/* APPLICATION NAVIGATION */}
                {/* ========================================= */}

                <nav className="border-b border-slate-700 bg-slate-950">
                    <div className="flex items-center gap-2 px-6 py-3">

                        <Link
                            href="/live"
                            className="
                                rounded-md
                                px-4
                                py-2
                                text-sm
                                font-medium
                                text-slate-200
                                hover:bg-slate-800
                                hover:text-white
                            "
                        >
                            Live
                        </Link>

                        <Link
                            href="/replay"
                            className="
                                rounded-md
                                px-4
                                py-2
                                text-sm
                                font-medium
                                text-slate-200
                                hover:bg-slate-800
                                hover:text-white
                            "
                        >
                            Replay
                        </Link>

                    </div>
                </nav>

                {/* ========================================= */}
                {/* PAGE CONTENT */}
                {/* ========================================= */}

                {children}

            </body>
        </html>
    );
}