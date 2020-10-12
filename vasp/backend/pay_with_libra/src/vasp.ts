import axios, { AxiosInstance } from "axios";
import { Currency } from "@libra/client";

export interface PaymentOption {
  address: string;
  currency: Currency;
  amount: number;
  paymentLink: string;
}

export interface PaymentOptions {
  paymentId: string;
  fiatPrice: number;
  fiatCurrency: string;
  options: PaymentOption[];
}

export default class Vasp {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.REACT_APP_BACKEND_URL || "";
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
        //Authorization: `Bearer ${getAccessToken()}`,
      },
    });
  }

  public async getPaymentOptions(paymentId: string): Promise<PaymentOptions> {
    return {
      "fiatCurrency": "USD",
      "fiatPrice": 34250000,
      "options": [
        {
          "address": "tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5",
          "amount": 34250000,
          "currency": "Coin1",
          "paymentLink": "libra://tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5?c=Coin1&am=34250000"
        },
        {
          "address": "tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5",
          "amount": 31712966,
          "currency": "Coin2",
          "paymentLink": "libra://tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5?c=Coin2&am=31712966"
        },
        {
          "address": "tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5",
          "amount": 32932676,
          "currency": "LBR",
          "paymentLink": "libra://tlb1px0gsvlknj5z3kgxqe6jt3rdh38t3hxyewl7tmcg69kly5?c=LBR&am=32932676"
        }
      ],
      "paymentId": "32bf63df-8498-4d44-a6f5-ecf969de207a"
    }

    const response = await this.client.get(`/payments/${paymentId}`);
    return {
      paymentId: response.data.payment_id,
      fiatPrice: response.data.fiat_price,
      fiatCurrency: response.data.fiat_currency,
      options: response.data.options.map((op: any) => ({
        address: op.address,
        currency: op.currency,
        amount: op.amount,
        paymentLink: op.payment_link,
      })),
    };
  }
}
