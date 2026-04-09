import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, Send, Loader2 } from 'lucide-react'
import { useX402 } from '../../hooks/useX402'
import { PaymentModal } from '../payment/PaymentModal'
import { TASK_TYPES } from '../../utils/constants'

interface Props {
  onResult: (taskId: string) => void
}

export function TaskSubmitter({ onResult }: Props) {
  const { submitTask, loading, paymentRequest, confirmPayment } = useX402()
  const [taskType, setTaskType] = useState<string>('summarize')
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const pdf = acceptedFiles.find((f) => f.type === 'application/pdf')
    if (pdf) setFile(pdf)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  })

  const handleSubmit = async () => {
    if (!prompt.trim()) return
    const result = await submitTask(taskType, prompt, file ?? undefined)
    if (result?.success && result.data) {
      const data = result.data as { task_id: string }
      onResult(data.task_id)
    }
  }

  return (
    <>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-5">
        {/* Task type selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
          <div className="grid grid-cols-3 gap-2">
            {TASK_TYPES.map((t) => (
              <button
                key={t.value}
                onClick={() => setTaskType(t.value)}
                className={`py-2.5 px-3 rounded-xl border text-sm font-medium transition text-left ${
                  taskType === t.value
                    ? 'border-blue-600 bg-blue-50 text-blue-700'
                    : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <div className="font-semibold">{t.label}</div>
                <div className="text-xs opacity-70 mt-0.5">{t.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* PDF upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Document (optional)
          </label>
          {file ? (
            <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-xl">
              <FileText className="w-5 h-5 text-blue-600 shrink-0" />
              <span className="text-sm text-blue-700 flex-1 truncate">{file.name}</span>
              <button
                onClick={() => setFile(null)}
                className="text-blue-400 hover:text-blue-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition ${
                isDragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-6 h-6 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                {isDragActive ? 'Drop PDF here...' : 'Drag & drop a PDF, or click to select'}
              </p>
              <p className="text-xs text-gray-400 mt-1">PDF only, max 10MB</p>
            </div>
          )}
        </div>

        {/* Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want to extract, summarize, or analyze..."
            rows={4}
            className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading || !prompt.trim()}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl px-4 py-3 text-sm font-medium transition"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Submit Task
            </>
          )}
        </button>
      </div>

      <PaymentModal
        open={!!paymentRequest}
        amountAlgo={paymentRequest?.amount_algo ?? 0}
        isCached={paymentRequest?.is_cached ?? false}
        onConfirm={() => confirmPayment(true)}
        onCancel={() => confirmPayment(false)}
      />
    </>
  )
}
