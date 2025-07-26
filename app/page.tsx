"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Upload, Download } from "lucide-react"

const PROMPT_OPTIONS = {
  "comic-book": {
    name: "Comic Book Style",
    description: "Bold lines, stylized shadows, dynamic expressions",
  },
  sketch: {
    name: "Sketch Style",
    description: "Refined, hand-drawn pencil-like detailing",
  },
  "childrens-cartoon": {
    name: "Children's Cartoon Style",
    description: "Soft, rounded features and playful charm",
  },
  "basic-outline": {
    name: "Photo Outline Style",
    description: "Simplified black-and-white outline of the actual photo",
  },
  caricature: {
    name: "Caricature Style",
    description: "Whimsical, bouncy line art with exaggerated character",
  },
}

export default function Home() {
  const [selectedPrompt, setSelectedPrompt] = useState("")
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files)
    setError("")
    setSuccess("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedPrompt) {
      setError("Please select a coloring book style")
      return
    }

    if (!selectedFiles || selectedFiles.length === 0) {
      setError("Please select at least one image")
      return
    }

    setIsProcessing(true)
    setError("")
    setSuccess("")

    try {
      const formData = new FormData()
      formData.append("prompt", selectedPrompt)

      // Add all selected files
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append("images", selectedFiles[i])
      }

      const response = await fetch("/api/process-images", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        // Handle zip file download
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `ColoringBook_${selectedPrompt.replace("-", "_")}.zip`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)

        setSuccess(`Successfully processed ${selectedFiles.length} image(s)! Download should start automatically.`)
      } else {
        const errorData = await response.json()
        setError(errorData.error || "Failed to process images")
      }
    } catch (err) {
      setError("Network error. Please try again.")
      console.error("Error:", err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl text-center">🎨 Coloring Book API Test</CardTitle>
            <p className="text-center text-gray-600">Upload images and convert them to coloring book pages</p>
          </CardHeader>

          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Style Selection */}
              <div className="space-y-2">
                <Label htmlFor="style">Select Coloring Book Style</Label>
                <Select value={selectedPrompt} onValueChange={setSelectedPrompt}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a style..." />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(PROMPT_OPTIONS).map(([key, value]) => (
                      <SelectItem key={key} value={key}>
                        <div>
                          <div className="font-medium">{value.name}</div>
                          <div className="text-sm text-gray-500">{value.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* File Upload */}
              <div className="space-y-2">
                <Label htmlFor="images">Upload Images</Label>
                <Input
                  id="images"
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileChange}
                  className="cursor-pointer"
                />
                <p className="text-sm text-gray-500">Select one or more images (JPG, PNG, WebP)</p>
                {selectedFiles && <p className="text-sm text-blue-600">{selectedFiles.length} file(s) selected</p>}
              </div>

              {/* Submit Button */}
              <Button type="submit" disabled={isProcessing || !selectedPrompt || !selectedFiles} className="w-full">
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing Images...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Convert to Coloring Book
                  </>
                )}
              </Button>
            </form>

            {/* Error Message */}
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Success Message */}
            {success && (
              <Alert className="border-green-200 bg-green-50">
                <Download className="h-4 w-4" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            {/* API Status */}
            <div className="pt-4 border-t">
              <h3 className="font-medium mb-2">API Status</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Health:</span>
                  <span className="ml-2 text-green-600">✓ Online</span>
                </div>
                <div>
                  <span className="text-gray-500">Styles:</span>
                  <span className="ml-2 text-green-600">✓ 5 Available</span>
                </div>
              </div>

              {/* Quick API Links */}
              <div className="mt-4 space-y-2">
                <h4 className="font-medium text-sm">Quick API Tests:</h4>
                <div className="flex gap-2">
                  <a
                    href="/api/health"
                    target="_blank"
                    className="text-xs bg-blue-100 hover:bg-blue-200 px-2 py-1 rounded"
                    rel="noreferrer"
                  >
                    Health Check
                  </a>
                  <a
                    href="/api/prompts"
                    target="_blank"
                    className="text-xs bg-green-100 hover:bg-green-200 px-2 py-1 rounded"
                    rel="noreferrer"
                  >
                    View Prompts
                  </a>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
