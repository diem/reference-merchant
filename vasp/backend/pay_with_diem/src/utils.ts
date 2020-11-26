import { PaymentType } from "./blockchainService";
// FIXME: DM
import { Currency } from "@libra/client";

const FIAT_MAX_FRACTION_DIGITS = 6;
const FIAT_SCALING_FACTOR = Math.pow(10, FIAT_MAX_FRACTION_DIGITS);
const DIEM_MAX_FRACTION_DIGITS = 6;
const DIEM_SCALING_FACTOR = Math.pow(10, DIEM_MAX_FRACTION_DIGITS);

const FIAT_VISUAL_FORMAT = {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
};

const DIEM_VISUAL_FORMAT = {
  minimumFractionDigits: 0,
  maximumFractionDigits: 6,
};

export function fiatToFloat(amount: number): number {
  return Math.trunc(amount) / FIAT_SCALING_FACTOR;
}

export function diemToFloat(amount: number): number {
  return Math.trunc(amount) / DIEM_SCALING_FACTOR;
}

/**
 * Convert the fiat amount from its internal representation to a human
 * readable decimal fraction.
 *
 * Fiat amounts are handled internally as fixed point scaled numbers and are
 * converted to decimal fraction only for UI presentation.
 *
 * @param amount  Fixed point scaled fiat amount.
 */
export function fiatToHumanFriendly(amount: number): string {
  return fiatToFloat(amount).toLocaleString(undefined, {
    ...FIAT_VISUAL_FORMAT,
    useGrouping: true,
  });
}

/**
 * Convert the Diem amount from its internal representation to a human
 * readable decimal fraction.
 *
 * Diem amounts are handled internally as fixed point scaled numbers and are
 * converted to decimal fraction only for UI presentation.
 *
 * @param amount  Fixed point scaled Diem amount.
 */
export function diemToHumanFriendly(amount: number): string {
  return diemToFloat(amount).toLocaleString(undefined, {
    ...DIEM_VISUAL_FORMAT,
    useGrouping: true,
  });
}

export function createWalletLink(
  protocol: string,
  paymentType: PaymentType,
  address: string,
  currency?: Currency,
  amount?: number
) {
  const paymentURL = new URL(`${protocol}://${address}`);

  if (currency) paymentURL.searchParams.set("currency", currency);
  if (amount) paymentURL.searchParams.set("amount", amount.toString());

  paymentURL.searchParams.set("paymentType", paymentType);

  return paymentURL;
}

export function createWebLink(
  link: string,
  paymentType: "onetime" | "recurring" | "subscription",
  address: string,
  currency?: Currency,
  amount?: number
) {
  const paymentURL = new URL(link);

  paymentURL.searchParams.set("address", address);

  if (currency) paymentURL.searchParams.set("currency", currency);
  if (amount) paymentURL.searchParams.set("amount", amount.toString());

  paymentURL.searchParams.set("paymentType", paymentType);

  return paymentURL;
}
