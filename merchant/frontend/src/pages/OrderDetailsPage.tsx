import React from "react";
import { useParams } from "react-router";
import OrderDetails from "../components/OrderDetails";

function OrderDetailsPage() {
  const { orderId } = useParams();
  return <OrderDetails orderId={orderId} />;
}

export default OrderDetailsPage;
