// src/components/Playground.tsx
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  useChatInteract,
  useChatMessages,
  IStep,
} from "@chainlit/react-client";
import { useEffect, useState } from "react";
import { SidebarTrigger, useSidebar } from "./ui/sidebar";
import { SimpleFileUpload } from "./ui/file-upload";
import { UploadedFileItem } from "./ui/uploaded-file-item";
import { FileDropzone } from "./ui/file-dropzone";

export function Playground() {
  const [inputValue, setInputValue] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();
  const { open, isMobile } = useSidebar();

  const handleSendMessage = () => {
    const content = inputValue.trim();
    if (content) {
      const message = {
        name: "user",
        type: "user_message" as const,
        output: content,
        // file: uploadedFiles,
      };
      sendMessage(message, []);
      setInputValue("");
      // setUploadedFiles([]);
    }
  };

  const handleFileUpload = (files: File[]) => {
    setUploadedFiles((prevFiles) => [...prevFiles, ...files]);
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      console.log(uploadedFiles);
    }, 1000);

    return () => clearTimeout(timeoutId);
  }, [uploadedFiles]);

  const handleRemoveFile = (fileToRemove: File) => {
    setUploadedFiles((prevFiles) =>
      prevFiles.filter((file) => file !== fileToRemove)
    );
  };

  const formatFileSize = (size: number) => {
    const units = ["B", "KB", "MB", "GB", "TB"];
    let unitIndex = 0;
    let fileSize = size;

    while (fileSize >= 1024 && unitIndex < units.length - 1) {
      fileSize /= 1024;
      unitIndex++;
    }

    return `${fileSize.toFixed(2)} ${units[unitIndex]}`;
  };

  const renderMessage = (message: IStep) => {
    const dateOptions: Intl.DateTimeFormatOptions = {
      hour: "2-digit",
      minute: "2-digit",
    };
    const date = new Date(message.createdAt).toLocaleTimeString(
      undefined,
      dateOptions
    );
    return (
      <div
        key={message.id}
        className={`flex items-start space-x-2 ${
          message.name === "Assistant" ? "" : "flex-row-reverse gap-4"
        }`}>
        <div
          className={`text-sm ${
            message.name === "user"
              ? "text-blue-500 ml-4"
              : "text-green-500 mr-4"
          }`}>
          {message.name}
        </div>
        <div className="border bg-black/5 rounded-lg p-2 w-fit pr-4 pl-4">
          <p className="text-black dark:text-white text-pretty">
            {message.output}
          </p>
          <small className="text-xs text-gray-500">{date}</small>
        </div>
      </div>
    );
  };

  return (
    <FileDropzone onDrop={handleFileUpload}>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col max-h-[100lvh]">
        <div className="sm:pl-4 sm:pt-4 p-1.5 sm:p-0 max-sm:shadow-md">
          {!isMobile && !open && <SidebarTrigger />}
          {isMobile && <SidebarTrigger />}
        </div>
        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-4">
            {messages.map((message) => renderMessage(message))}
          </div>
        </div>
        <div className="border-t p-4 bg-white dark:bg-gray-800">
          {uploadedFiles.length > 0 && (
            <div className="mb-4">
              <ul>
                {uploadedFiles.map((file, index) => (
                  <UploadedFileItem
                    key={index}
                    file={file}
                    fileSize={formatFileSize(file.size)}
                    onRemove={handleRemoveFile} // Passer la fonction de suppression ici
                  />
                ))}
              </ul>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <SimpleFileUpload onChange={handleFileUpload} />
            <Input
              autoFocus
              className="flex-1"
              id="message-input"
              placeholder="Envoyer un message"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyUp={(e) => {
                if (e.key === "Enter") {
                  handleSendMessage();
                }
              }}
            />
            <Button onClick={handleSendMessage} type="submit">
              Envoyer
            </Button>
          </div>
        </div>
      </div>
    </FileDropzone>
  );
}
