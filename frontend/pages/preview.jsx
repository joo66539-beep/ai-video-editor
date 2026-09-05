import { useEffect, useState } from 'react'
import axios from 'axios'
import { useRouter } from 'next/router'

export default function Preview() {
  const router = useRouter()
  const { job } = router.query
  const [data, setData] = useState(null)

  useEffect(() => {
    async function fetchJob() {
      if (!job) return
      try {
        const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const res = await axios.get(`${api}/job/${job}`)
        setData(res.data)
      } catch (err) {
        console.error(err)
      }
    }
    fetchJob()
  }, [job])

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">معاينة النتائج</h2>
        {!data && <p>أدخل المهمة لعرض النتائج أو ضع رابطًا من الرفع.</p>}
        {data && (
          <div>
            <h3 className="font-bold">مشاهد مقترحة</h3>
            <pre className="bg-gray-100 p-3 rounded mt-2">{JSON.stringify(data.scenes, null, 2)}</pre>
            <h3 className="font-bold mt-4">الترجمة</h3>
            <pre className="bg-gray-100 p-3 rounded mt-2">{data.subtitles}</pre>
          </div>
        )}
      </div>
    </div>
  )
}
