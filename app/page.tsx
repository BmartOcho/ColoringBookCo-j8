export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center mb-6">Coloring Book API</h1>

        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">API Endpoints:</h2>
            <ul className="space-y-2 text-sm">
              <li>
                <code className="bg-gray-100 px-2 py-1 rounded">GET /api/health</code> - Health check
              </li>
              <li>
                <code className="bg-gray-100 px-2 py-1 rounded">GET /api/prompts</code> - Available prompt styles
              </li>
              <li>
                <code className="bg-gray-100 px-2 py-1 rounded">POST /api/process-images</code> - Process images
              </li>
            </ul>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Available Styles:</h2>
            <ul className="space-y-1 text-sm">
              <li>
                • <strong>comic-book</strong> - Bold lines, stylized shadows, dynamic expressions
              </li>
              <li>
                • <strong>sketch</strong> - Refined, hand-drawn pencil-like detailing
              </li>
              <li>
                • <strong>childrens-cartoon</strong> - Soft, rounded features and playful charm
              </li>
              <li>
                • <strong>basic-outline</strong> - Simplified black-and-white outline
              </li>
              <li>
                • <strong>caricature</strong> - Whimsical, bouncy line art with exaggerated character
              </li>
            </ul>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Usage:</h2>
            <p className="text-sm">
              Send POST requests to <code className="bg-gray-100 px-1 rounded">/api/process-images</code> with:
            </p>
            <ul className="text-sm mt-2 space-y-1">
              <li>
                • <code>prompt</code>: One of the style keys above
              </li>
              <li>
                • <code>images</code>: Multiple image files
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
