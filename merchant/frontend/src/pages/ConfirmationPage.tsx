import React from "react";
import { useParams } from "react-router";
import ConfirmationDetails from "../components/ConfirmationDetails";

function ConfirmationPage() {
  const { orderId } = useParams();
  return <ConfirmationDetails orderId={orderId} />;
}

export default ConfirmationPage;
