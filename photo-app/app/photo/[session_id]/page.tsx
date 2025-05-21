'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import Image from 'next/image'

export default function PhotoPage({ params }: { params: { session_id: string } }) {
  const [photos, setPhotos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const { session_id } = params

  useEffect(() => {
    async function fetchPhotos() {
      try {
        setLoading(true)
        
        // Fetch photos for this session from Supabase
        const { data, error } = await supabase
          .from('photos')
          .select('*')
          .eq('session_id', session_id)
          .order('created_at', { ascending: false })
        
        if (error) {
          throw error
        }
        
        if (data) {
          setPhotos(data)
        }
      } catch (error) {
        console.error('Error fetching photos:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchPhotos()
  }, [session_id])
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }
  
  if (photos.length === 0) {
    return <div className="flex items-center justify-center min-h-screen">No photos found for this session</div>
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Photos from Your Session</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {photos.map((photo) => (
          <div key={photo.id} className="border rounded-lg overflow-hidden shadow-lg">
            <div className="relative h-64 w-full">
              <Image 
                src={photo.url} 
                alt="Photo" 
                fill 
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                className="object-cover"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}