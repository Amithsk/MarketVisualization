"use client";

import {

    useState

} from "react";

type Props = {

    selectedStock: string;

    disabled?: boolean;

    onUploadSuccess?: () => void;
};

export default function UploadPanel({

    selectedStock,

    disabled = false,

    onUploadSuccess

}: Props) {

    // -----------------------------------
    // State
    // -----------------------------------

    const [selectedFile, setSelectedFile] =
        useState<File | null>(null);

    const [uploading, setUploading] =
        useState(false);

    const [successMessage, setSuccessMessage] =
        useState("");

    const [errorMessage, setErrorMessage] =
        useState("");

    // -----------------------------------
    // File Change
    // -----------------------------------

    const handleFileChange = (
        event:
        React.ChangeEvent<HTMLInputElement>
    ) => {

        const files =
            event.target.files;

        if (
            !files ||
            files.length === 0
        ) {
            return;
        }

        setSelectedFile(
            files[0]
        );

        setSuccessMessage("");

        setErrorMessage("");
    };

    // -----------------------------------
    // Upload File
    // -----------------------------------

    const handleUpload = async () => {

        if (!selectedFile) {

            alert(
                "Select a file first"
            );

            return;
        }

        try {

            setUploading(true);

            setSuccessMessage("");

            setErrorMessage("");

            const formData =
                new FormData();

            formData.append(
                "file",
                selectedFile
            );

            const response =
                await fetch(

                    "http://127.0.0.1:8000/api/v1/upload/stock-candles",

                    {
                        method: "POST",

                        body: formData
                    }
                );

            const result =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    result.message ||
                    "Upload failed"
                );
            }

            setSuccessMessage(
                `${selectedStock} uploaded successfully`
            );

            if (onUploadSuccess) {

                onUploadSuccess();
            }

        } catch (error: any) {

            console.error(error);

            setErrorMessage(

                error.message ||

                "Upload failed"
            );

        } finally {

            setUploading(false);
        }
    };

    return (

        <div
            className="
                bg-gray-900
                border
                border-gray-800
                rounded-lg
                p-4
                flex
                flex-col
                gap-4
                min-w-[320px]
            "
        >

            {/* -------------------------------- */}
            {/* Title */}
            {/* -------------------------------- */}

            <div>

                <h2
                    className="
                        text-lg
                        font-semibold
                    "
                >

                    Upload Stock Candles

                </h2>

            </div>

            {/* -------------------------------- */}
            {/* Selected Stock */}
            {/* -------------------------------- */}

            <div
                className="
                    text-sm
                    text-gray-400
                "
            >

                Selected Stock:

                <span
                    className="
                        text-white
                        ml-2
                    "
                >

                    {

                        selectedStock ||

                        "None"
                    }

                </span>

            </div>

            {/* -------------------------------- */}
            {/* File Input */}
            {/* -------------------------------- */}

            <input

                type="file"

                accept=".csv,.xlsx,.xls"

                disabled={
                    disabled ||
                    uploading
                }

                onChange={
                    handleFileChange
                }

                className="
                    text-sm
                    text-gray-300
                "
            />

            {/* -------------------------------- */}
            {/* Upload Button */}
            {/* -------------------------------- */}

            <button

                onClick={
                    handleUpload
                }

                disabled={
                    disabled ||
                    uploading ||
                    !selectedFile
                }

                className="
                    bg-green-600
                    hover:bg-green-700
                    disabled:bg-gray-700
                    disabled:cursor-not-allowed
                    px-4
                    py-2
                    rounded-md
                    text-sm
                    font-medium
                "
            >

                {

                    uploading

                        ? "Uploading..."

                        : "Upload File"
                }

            </button>

            {/* -------------------------------- */}
            {/* Success */}
            {/* -------------------------------- */}

            {

                successMessage && (

                    <div
                        className="
                            text-green-400
                            text-sm
                        "
                    >

                        {

                            successMessage
                        }

                    </div>
                )
            }

            {/* -------------------------------- */}
            {/* Error */}
            {/* -------------------------------- */}

            {

                errorMessage && (

                    <div
                        className="
                            text-red-400
                            text-sm
                        "
                    >

                        {

                            errorMessage
                        }

                    </div>
                )
            }

        </div>
    );
}