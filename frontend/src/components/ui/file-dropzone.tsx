// src/components/ui/FileDropzone.tsx
import React, { useCallback } from "react";

interface FileDropzoneProps {
  onDrop: (files: File[]) => void;
  children: React.ReactNode;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onDrop,
  children,
}) => {
  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      const files = Array.from(event.dataTransfer.files);
      onDrop(files);
    },
    [onDrop]
  );

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  return (
    <div onDrop={handleDrop} onDragOver={handleDragOver} className="">
      {children}
    </div>
  );
};
