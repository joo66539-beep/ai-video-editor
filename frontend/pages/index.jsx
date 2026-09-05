import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-3xl w-full p-8 bg-white rounded shadow">
        <h1 className="text-2xl font-bold mb-4">محرر الفيديو بالذكاء الاصطناعي</h1>
        <p className="mb-6">تحميل فيديو، كشف المشاهد، ترجمة آلية ومقترحات قصّات. نسخة تجريبية.</p>
        <div className="flex gap-4">
          <Link href="/upload"><a className="px-4 py-2 bg-blue-600 text-white rounded">ارفع فيديو</a></Link>
          <Link href="/preview"><a className="px-4 py-2 border rounded">عرض المعاينة</a></Link>
        </div>
      </div>
    </div>
  )
}
