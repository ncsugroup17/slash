import { ProductCard } from "@/components/product-card"

interface ProductGridProps {
  products: Array<{
    id: string;
    title: string;
    img?: string;
    price: string;
    website: string;
    rating: string;
    link: string;
  }>;
}

export function ProductGrid({ products }: ProductGridProps) {
  if (!products.length) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No products found</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
} 