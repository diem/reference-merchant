export type FiatCurrency = "USD" | "EUR";

export type PaymentType = "direct"

export interface Product {
  gtin: string;
  name: string;
  description: string;
  price: number;
  currency: FiatCurrency;
  payment_type: PaymentType;
  image_url: string;
}
