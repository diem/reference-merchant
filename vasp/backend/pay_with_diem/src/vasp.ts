import axios, { AxiosInstance } from "axios";
// FIXME: DM
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
  walletURL: string;
  baseMerchantURL: string;
}

export default class Vasp {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.REACT_APP_BACKEND_URL || "/vasp";
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
        //Authorization: `Bearer ${getAccessToken()}`,
      },
    });
  }

  public async getPaymentOptions(paymentId: string): Promise<PaymentOptions> {
    const response = await this.client.get(`/payments/${paymentId}`);
    return {
      paymentId: response.data.payment_id,
      fiatPrice: response.data.fiat_price,
      fiatCurrency: response.data.fiat_currency,
      walletURL: response.data.wallet_url,
      baseMerchantURL: response.data.base_merchant_url,
      options: response.data.options.map((op: any) => ({
        address: op.address,
        currency: op.currency,
        amount: op.amount,
        paymentLink: op.payment_link,
      })),
    };
  }
}
