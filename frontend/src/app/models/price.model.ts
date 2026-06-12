export interface Product {
  product_id: string;
  name: string;
  price: number;
  old_price: number;
  discount_pct: number;
  rating: number;
  currency: string;
  category: string;
  source: string;
  scraped_at: string;
  image_url: string;
  url: string;
}

export interface SourceStats {
  source: string;
  total_products: number;
  avg_price: number;
  min_price: number;
  max_price: number;
  avg_discount: number;
}
