import { FileTextIcon, TrashIcon } from "lucide-react";

interface UploadedFileItemProps {
  file: File;
  fileSize: string;
  onRemove: (file: File) => void; // Ajouter la prop onRemove
}

export const UploadedFileItem = ({
  file,
  fileSize,
  onRemove,
}: UploadedFileItemProps) => {
  // Extraire l'extension du fichier
  const fileExtension = file.name.split(".").pop()?.toUpperCase();

  return (
    <>
      <li className="flex items-center justify-between p-2 border border-gray-300 dark:border-gray-700 rounded-lg mt-2 bg-white dark:bg-gray-800 shadow-sm">
        <div className="flex items-center">
          <FileTextIcon
            className="text-gray-500 dark:text-gray-400 mr-2"
            height={20}
            width={20}
          />
          <div className="flex flex-col flex-1">
            <span className="sm:text-sm text-xs font-medium text-gray-900 dark:text-gray-200 truncate overflow-hidden whitespace-nowrap">
              {file.name}
            </span>
            <span className="sm:text-xs text-[10px] text-gray-500 dark:text-gray-400">
              {fileSize}
            </span>
          </div>
        </div>
        <div className="flex items-center">
          {fileExtension && (
            <span className="text-xs text-gray-500 dark:text-gray-400 ml-4 whitespace-nowrap">
              {fileExtension}
            </span>
          )}
          <button
            onClick={() => onRemove(file)} // Appeler la fonction onRemove
            className="ml-4 p-1 text-red-500 hover:text-red-700 transition-colors"
            aria-label={`Remove ${file.name}`}>
            <TrashIcon height={20} width={20} />
          </button>
        </div>
      </li>
    </>
  );
};
