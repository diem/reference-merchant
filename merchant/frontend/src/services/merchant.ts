import axios, { AxiosInstance } from "axios";
import { Product } from "../interfaces/product";

export type PaymentEventType =
  | "created"
  | "cleared"
  | "rejected"
  | "error"
  | "payout_processing"
  | "payout_completed";

export interface PaymentEvent {
  timestamp: Date;
  eventType: PaymentEventType;
}

export interface BlockchainTx {
  transactionId: number;
  isRefund: boolean;
  senderAddress: string;
  amount: number;
  currency: string;
}

export interface PaymentDetailedStatus {
  status: PaymentEventType;
  merchantAddress: string;
  canCashOut: boolean;
  canRefund: boolean;
  events: PaymentEvent[];
  blockchainTxs: BlockchainTx[];
}

export interface PaymentProcessingDetails {
  paymentFormUrl: string;
  vaspPaymentId: string;
  orderId: string;
}

export interface ProductOrder {
  product: Product;
  quantity: number;
}

export interface Order {
  orderId: string;
  createdAt: Date;
  vaspPaymentRef: string;
  totalPrice: number;
  currency: string;
  products: ProductOrder[];
  paymentStatus: PaymentDetailedStatus;
  image_url?: string;
}

export default class BackendClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.REACT_APP_BACKEND_URL || "/api";
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
        //Authorization: `Bearer ${getAccessToken()}`,
      },
    });
  }

  public async getProductsList(): Promise<Product[]> {
    const response = await this.client.get("/products");
    return response.data.products;
  }

  public async checkoutOne(gtin: string): Promise<PaymentProcessingDetails> {
    const order = {
      items: [{ gtin, quantity: 1 }],
    };
    const response = await this.client.post("/payments", order);
    return {
      orderId: response.data.order_id,
      vaspPaymentId: response.data.vasp_payment_id,
      paymentFormUrl: `${response.data.payment_form_url}&orderId=${response.data.order_id}`,
    };
  }

  public async getPaymentLog(payment_id: string): Promise<PaymentDetailedStatus | null> {
    try {
      const response = await this.client.get(`/payments/${payment_id}/log`);

      return {
        status: response.data.status,
        merchantAddress: response.data.merchant_address,
        canCashOut: response.data.can_payout,
        canRefund: response.data.can_refund,
        events: response.data.events.map((ev) => ({
          timestamp: new Date(ev.timestamp),
          eventType: ev.event_type,
        })),
        blockchainTxs: response.data.chain_txs.map(
          (tx) =>
            <BlockchainTx>{
              senderAddress: tx.sender_address,
              amount: tx.amount,
              currency: tx.currency,
              transactionId: tx.tx_id,
              isRefund: tx.is_refund,
            }
        ),
      };
    } catch (e) {
      if (e.response?.status === 404) {
        return null;
      }
      throw e;
    }
  }

  public async getPaymentStatus(order_id: string): Promise<string> {
    try {
      const response = await this.client.get(`/orders/${order_id}/payment`);

      return response.data.status;
    } catch (e) {
      if (e.response?.status === 404) {
        return "Unknown";
      }
      console.error(e);
      console.error(e.response);
      throw e;
    }
  }

  public async getOrderDetails(order_id: string): Promise<Order | null> {
    try {
      const response = await this.client.get(`/orders/${order_id}`);

      return {
        orderId: response.data.order_id,
        createdAt: new Date(response.data.created_at),
        vaspPaymentRef: response.data.vasp_payment_reference,
        totalPrice: response.data.total_price,
        currency: response.data.currency,
        products: response.data.products,
        paymentStatus: {
          status: response.data.payment_status.status,
          merchantAddress: response.data.payment_status.merchant_address,
          canCashOut: response.data.payment_status.can_payout,
          canRefund: response.data.payment_status.can_refund,
          events: response.data.payment_status.events.map((ev) => ({
            timestamp: new Date(ev.timestamp),
            eventType: ev.event_type,
          })),
          blockchainTxs: response.data.payment_status.chain_txs.map((tx) => ({
            transactionId: tx.tx_id,
            isRefund: tx.is_refund,
            senderAddress: tx.sender_address,
            amount: tx.amount,
            currency: tx.currency,
          })),
        },
      };
    } catch (e) {
      if (e.response?.status === 404) {
        return null;
      }
      console.error(e);
      console.error(e.response);
      throw e;
    }
  }

  public async payout(paymentId: string) {
    await this.client.post(`/payments/${paymentId}/payout`);
  }

  public async refund(paymentId: string) {
    await this.client.post(`/payments/${paymentId}/refund`);
  }
}
