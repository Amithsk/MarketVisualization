import path from "path";

import type {
    NextConfig
} from "next";

const nextConfig: NextConfig = {

    outputFileTracingRoot:
        path.join(__dirname),

    async rewrites() {
        return [
            {
                source: "/api/v1/:path*",
                destination: "http://127.0.0.1:8003/api/v1/:path*",
            },
        ];
    },

};

export default nextConfig;