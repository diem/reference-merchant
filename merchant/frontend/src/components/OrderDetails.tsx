import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import BackendClient, { Order } from "../services/merchant";
import { Alert, Button, Container, Spinner } from "reactstrap";
import InfoField from "./InfoField";
import OrderProducts from "./OrderProducts";
import LinkField from "./LinkField";
import PaymentEvents from "./PaymentEvents";

export interface OrderDetailsProps {
  orderId: string;
}

function OrderDetails({ orderId }: OrderDetailsProps) {
  const { t } = useTranslation("order");
  const [order, setOrder] = useState<Order | undefined | null>();

  const tx =
    order && order.paymentStatus.blockchainTxs.length > 0
      ? order.paymentStatus.blockchainTxs[0]
      : null;
  const refundTx =
    order &&
    order.paymentStatus.blockchainTxs.length > 1 &&
    order.paymentStatus.blockchainTxs[1].isRefund
      ? order.paymentStatus.blockchainTxs[1]
      : null;

  useEffect(() => {
    let isOutdated = false;

    const fetchOrder = async () => {
      try {
        const fetched = await new BackendClient().getOrderDetails(orderId);

        if (!isOutdated) {
          setOrder(fetched);
        }
      } catch (e) {
        console.error("Unexpected error", e);
      }
    };

    // noinspection JSIgnoredPromiseFromCall
    fetchOrder();

    return () => {
      isOutdated = true;
    };
  }, [orderId]);

  const cashOut = async () => {
    const client = new BackendClient();
    await client.payout(order!.vaspPaymentRef);
    const fetched = await new BackendClient().getOrderDetails(orderId);
    if (fetched) {
      setOrder(fetched);
    }
  };

  const refund = async () => {
    const client = new BackendClient();
    await client.refund(order!.vaspPaymentRef);
    const fetched = await new BackendClient().getOrderDetails(orderId);
    if (fetched) {
      setOrder(fetched);
    }
  };

  // Show spinner if order is undefined - it is being loaded
  let orderInfo = (
    <div className="d-flex justify-content-center">
      <Spinner color="primary" />
    </div>
  );

  if (order !== undefined) {
    if (order === null) {
      // There is no order with this ID
      orderInfo = (
        <Alert color="danger">
          <i className="fa fa-close" /> {t("unknown")}
        </Alert>
      );
    } else {
      orderInfo = (
        <>
          <InfoField caption="Order ID" value={orderId.toUpperCase()} />
          <InfoField caption="Creation time" value={order.createdAt.toLocaleString()} />
          <InfoField caption="Current status" value={t(`status.${order?.paymentStatus.status}`)} />

          <div className="mt-5">
            <OrderProducts
              productOrders={order.products}
              total={order.totalPrice}
              currency={order.currency}
            />
          </div>

          <div className="mt-5">
            <h2 className="h5 font-weight-normal text-body">Payment details</h2>

            <InfoField caption="Payment ID" value={order.vaspPaymentRef.toUpperCase()} />
            <InfoField caption="Payment type" value="Direct" />
            <InfoField
              caption="Merchant Diem address"
              value={order.paymentStatus.merchantAddress}
            />
            <InfoField caption="Payer Diem address" value={tx ? tx.senderAddress : "N/A"} />
            <InfoField caption="Payer wallet type" value="Non-hosted" />
            <InfoField
              caption="Diem amount"
              value={tx ? `${tx.amount / 1000000} ${tx.currency}` : "N/A"}
            />

            <LinkField
              caption="Diem transaction ID"
              text={tx ? `${tx.transactionId}` : undefined}
              url={`https://diemexplorer.com/testnet/version/${tx?.transactionId}`}
              external
            />

            {refundTx && (
              <LinkField
                caption="Diem refund transaction ID"
                text={`${refundTx.transactionId}`}
                url={`https://diemexplorer.com/testnet/version/${refundTx.transactionId}`}
                external
              />
            )}

            <div className="mt-4">Payment events</div>
            <div className="mt-3">
              <PaymentEvents events={order.paymentStatus.events} />
            </div>

            <div className="d-flex justify-content-center m-2">
              <Button
                disabled={!order.paymentStatus.canCashOut}
                onClick={cashOut}
                className="m-2"
                color="primary"
              >
                Cash out
              </Button>
              <Button
                disabled={!order.paymentStatus.canRefund}
                onClick={refund}
                className="m-2"
                color="primary"
              >
                Refund
              </Button>
            </div>

            <div className="d-flex justify-content-center mt-5">
              <a href={`admin/order/${orderId}`} target="_blank" rel="noopener noreferrer">
                #permalink
              </a>
            </div>
          </div>
        </>
      );
    }
  }

  return (
    <Container className="container-narrow pt-5">
      <div className="text-center">
        <div className="h2">{t("title")}</div>
      </div>

      <div className="d-flex flex-column justify-content-center m-5">{orderInfo}</div>
    </Container>
  );
}

export default OrderDetails;
