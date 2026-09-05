import { useState } from 'react'
import axios from 'axios'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return alert('اختر ملفاً')
    setStatus('Uploading...')
    const form = new FormData()
    form.append('file', file)
    try {
      const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.post(`${api}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setStatus('Uploaded. Processing started.')
      console.log('response', res.data)
      // Navigate to preview with returned job id or data
      window.location.href = `/preview?job=${res.data.job_id || ''}`
    } catch (err) {
      console.error(err)
      setStatus('Upload failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full p-6 bg-white rounded shadow">
        <h2 className="text-xl font-semibold mb-4">رفع الفيديو</h2>
        <form onSubmit={handleUpload} className="space-y-4">
          <input type="file" accept="video/*" onChange={e=>setFile(e.target.files[0])} />
          <div>
            <button className="px-4 py-2 bg-green-600 text-white rounded">ارفع</button>
          </div>
          <div className="text-sm text-gray-600">{status}</div>
        </form>
      </div>
    </div>
  )
}
