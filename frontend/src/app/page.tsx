import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home(): React.JSX.Element {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-6">Welcome to Reports AI</h1>
        <Link href="/startupReports">
          <Button size="lg">View Startup Reports</Button>
        </Link>
      </div>
    </div>
  )
}
