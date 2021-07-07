import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import BackendClient, { Order } from "../services/merchant";
import { Alert, Container, Spinner, Col, Row } from "reactstrap";
import TestnetWarning from "../components/TestnetWarning";

export interface OrderDetailsProps {
  orderId: string;
}

function ConfirmationDetails({ orderId }: OrderDetailsProps) {
  const { t } = useTranslation(["order", "layout"]);
  const [order, setOrder] = useState<Order | undefined | null>();

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
          <div style={{ display: "flex", alignItems: "center" }}>
            <i className="fa fa-check-circle fa-4x" style={{ color: "#59a559" }} />
            <div style={{ marginLeft: 20, fontSize: 20, fontWeight: 500, color: "black" }}>
              {t("orderOnTheWay")}
            </div>
          </div>
          <div className="h5 mt-4 mb-4 font-weight-normal text-body">
            {t("gotYourOrder")} <br />
            {t("orderSummary")}
          </div>
          <Row style={{ alignItems: "center" }}>
            <Col xs={3}>
              <img
                src={order.products[0].product.image_url}
                width="75"
                height="75"
                alt={"product image"}
              />
            </Col>
            <Col>{order.products[0].product.name}</Col>
            <Col style={{ textAlign: "right" }}>
              {t("qty")}. {order.products[0].quantity}
            </Col>
          </Row>
          <Row className="mt-4">
            <Col xs={8}>{t("itemsTotal")}</Col>
            <Col xs={4} style={{ textAlign: "right" }}>
              {order.totalPrice / 1000000} XUS
            </Col>
          </Row>
          <Row className="mt-1">
            <Col xs={9}>{t("shipping")}</Col>
            <Col xs={3} className="pl-2">
              {t("free")}
            </Col>
          </Row>
          <Row className="mt-1">
            <Col xs={9}>{t("dutiesTaxes")}</Col>
            <Col xs={3} className="pl-2">
              {t("free")}
            </Col>
          </Row>
          <Row className="mt-1">
            <Col xs={8} className="font-weight-bold">
              {t("totalOrder")}
            </Col>
            <Col xs={4} style={{ textAlign: "right" }} className="font-weight-bold">
              {order.totalPrice / 1000000} XUS
            </Col>
          </Row>
        </>
      );
    }
  }

  return (
    <>
      <TestnetWarning />
      <Container className="container-very-narrow pt-5">
        <div className="text-center">
          <div className="h2">{t("layout:name")}</div>
        </div>
        <div className="d-flex flex-column justify-content-center m-3">{orderInfo}</div>
      </Container>
    </>
  );
}

export default ConfirmationDetails;
