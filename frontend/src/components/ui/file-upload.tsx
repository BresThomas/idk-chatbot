import { UploadIcon } from "lucide-react";
import { useRef, useState } from "react";

export const SimpleFileUpload = ({
  onChange,
}: {
  onChange?: (files: File[]) => void;
}) => {
  const [, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (newFiles: File[]) => {
    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    onChange && onChange(newFiles);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.pdf,.doc,.docx"
        multiple
        onChange={(e) => handleFileChange(Array.from(e.target.files || []))}
        className="hidden"
      />
      <div
        onClick={handleClick}
        className="cursor-pointer flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-800 mr-2">
        <UploadIcon height={16} width={16} />
      </div>
    </div>
  );
};
