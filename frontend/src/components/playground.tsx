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
import { Content } from "@radix-ui/react-dialog";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { auth } from "@/firebase/firebaseConfig";

export function Playground() {
  const [inputValue, setInputValue] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();
  const { open, isMobile } = useSidebar();
  const [selectedIcon, setSelectedIcon] = useState<{
    [key: string]: string | null;
  }>({});

  const handleIconClick = (messageId: string, iconType: "like" | "dislike") => {
    // Si l'icône cliquée est déjà sélectionnée, on la désélectionne
    if (selectedIcon[messageId] === iconType) {
      setSelectedIcon((prev) => ({ ...prev, [messageId]: null }));
    } else {
      setSelectedIcon({ [messageId]: iconType });
    }
  };

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

  const [profilePicture, setProfilePicture] = useState<string | null>(null);
  useEffect(() => {
    const user = auth.currentUser; // Get the current user
    if (user) {
      setProfilePicture(user.photoURL || "/img/avatar.svg"); // Use displayName or email as username
    }
  }, []);

  const renderMessage = (message: IStep) => {
    const dateOptions: Intl.DateTimeFormatOptions = {
      hour: "2-digit",
      minute: "2-digit",
    };
    const date = new Date(message.createdAt).toLocaleTimeString(
      undefined,
      dateOptions
    );

    const isLiked = selectedIcon[message.id] === "like";
    const isDisliked = selectedIcon[message.id] === "dislike";

    return (
      <div
        key={message.id}
        className={`flex items-start space-x-2 ${
          message.name === "Assistant" ? "" : "flex-row-reverse gap-3"
        }`}>
        <div
          className={`text-sm ${
            message.name === "user"
              ? "text-blue-500 ml-4"
              : "text-green-500 mr-4"
          }`}>
          {message.name === "user" ? (
            <div className="flex items-center">
              <img
                src={profilePicture ?? "/img/avatar.svg"}
                alt="userProfile"
                className="h-8 w-8 sm:h-16 sm:w-16 rounded-full"
              />
            </div>
          ) : (
            <img
              src="/img/claude-ai.svg"
              alt="Claude AI"
              className="h-8 w-8 sm:h-16 sm:w-16"
            />
          )}
        </div>
        <div className="border bg-black/5 rounded-lg p-2 w-fit pr-4 pl-4 relative sm:min-w-[110px]">
          <p className="text-black dark:text-white text-pretty">
            {message.output}
          </p>
          <small className="text-xs text-gray-500">{date}</small>
          <div
            className={`absolute top-[3.35rem] right-2 flex space-x-2 ${
              message.name === "Assistant"
                ? "flex-row-reverse gap-2 items-center"
                : ""
            }`}>
            <ThumbsUp
              className={`cursor-pointer h-5 w-5 ${
                isLiked ? "text-blue-500" : "text-gray-500"
              } hover:text-blue-500`}
              onClick={() => handleIconClick(message.id, "like")}
            />
            <ThumbsDown
              className={`cursor-pointer h-5 w-5 ${
                isDisliked ? "text-red-500" : "text-gray-500"
              } hover:text-red-500`}
              onClick={() => handleIconClick(message.id, "dislike")}
            />
          </div>
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
              className="flex-1 border-0.5 border-black"
              id="message-input"
              placeholder="Envoyer un message"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyUp={(e) => {
                if (e.key === "Enter") {
                  handleSendMessage();
                  console.log(Content);
                }
              }}
            />
            <Button
              onClick={handleSendMessage}
              type="submit"
              style={{
                background: "linear-gradient(120deg, #5391c1, #876bca)",
                color: "white",
              }}>
              Envoyer
            </Button>
          </div>
        </div>
      </div>
    </FileDropzone>
  );
}
