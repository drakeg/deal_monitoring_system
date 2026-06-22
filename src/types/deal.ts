export interface Deal {
  id: string;
  brand: string[];
  category: string;
  title: string;
  merchant: string;
  asin?: string;
  price: string;
  regularPrice?: string;
  discount?: string;
  affiliateUrl: string;
  imageUrl: string;
  whyItMatters: string;
  dealScore: number;
  status?: string;
  featured?: boolean;
  tags?: string[];
  lastChecked?: string;
}