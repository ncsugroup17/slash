import { Button } from "@/components/ui/button"
import { addToWishlist } from "@/lib/api"
import { useState } from "react"

interface ProductCardProps {
  product: {
    id: string;
    title: string;
    img?: string;
    price: string;
    website: string;
    rating: string;
    link: string;
  }
}

export function ProductCard({ product }: ProductCardProps) {
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false)
  const [addedToWishlist, setAddedToWishlist] = useState(false)

  const handleAddToWishlist = async () => {
    try {
      setIsAddingToWishlist(true)
      await addToWishlist({
        title: product.title,
        img: product.img,
        price: product.price,
        website: product.website,
        rating: product.rating,
      })
      setAddedToWishlist(true)
    } catch (error) {
      console.error("Error adding to wishlist:", error)
      alert("Failed to add item to wishlist. Please try again.")
    } finally {
      setIsAddingToWishlist(false)
    }
  }

  return (
    <div className="bg-card rounded-lg shadow overflow-hidden flex flex-col">
      <div className="aspect-square relative bg-muted">
        {product.img ? (
          <img 
            src={product.img} 
            alt={product.title}
            className="object-cover w-full h-full"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
            No image
          </div>
        )}
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-medium line-clamp-2 mb-2">{product.title}</h3>
        <div className="mt-auto space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Price:</span>
            <span className="font-medium">{product.price}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Website:</span>
            <span>{product.website}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Rating:</span>
            <span>{product.rating}</span>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2">
            <a href={product.link} target="_blank" rel="noopener noreferrer">
              <Button variant="outline" className="w-full" size="sm">
                View
              </Button>
            </a>
            <Button
              onClick={handleAddToWishlist}
              disabled={isAddingToWishlist || addedToWishlist}
              className="w-full"
              size="sm"
            >
              {addedToWishlist ? "Added" : isAddingToWishlist ? "Adding..." : "Wishlist"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
} 