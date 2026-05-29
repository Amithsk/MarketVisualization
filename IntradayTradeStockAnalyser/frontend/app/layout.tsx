/*IntradayTradeStockAnalyser/frontend/app/layout.tsx*/

import "./globals.css";

export const metadata = {

    title:
        "Intraday Replay System",

    description:
        "Context-aware replay platform",
};

export default function RootLayout({

    children,

}: {

    children:
        React.ReactNode
}) {

    return (

        <html lang="en">

            <body>

                {children}

            </body>

        </html>
    );
}