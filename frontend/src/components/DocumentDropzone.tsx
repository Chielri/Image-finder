import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface Props {
  file: File | null
  onFile: (file: File) => void
  label: string
  accept: Record<string, string[]>
}

export function DocumentDropzone({ file, onFile, label, accept }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length > 0) onFile(accepted[0])
    },
    [onFile],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple: false,
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-blue-500 bg-blue-50'
          : file
            ? 'border-green-400 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      <div className="text-sm text-gray-600">
        {file ? (
          <div>
            <div className="font-medium text-green-700 truncate max-w-xs mx-auto">{file.name}</div>
            <div className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</div>
          </div>
        ) : (
          <div>
            <div className="text-2xl mb-2">+</div>
            <div className="font-medium">{label}</div>
            <div className="text-xs text-gray-400 mt-1">Drop file here or click to browse</div>
          </div>
        )}
      </div>
    </div>
  )
}
