import React, { useEffect, useRef, useState } from "react";
import { Button, Modal, ModalBody, ModalHeader, Spinner } from "reactstrap";
import BackendClient, { PaymentProcessingDetails } from "../services/merchant";
import { Product } from "../interfaces/product";
import OrderDetails from "./OrderDetails";

export interface PaymentProps {
  product?: Product;
  isOpen: boolean;
  onClose: () => void;
}

export default function Payment({ product, isOpen, onClose }: PaymentProps) {
  const [paymentProcessingDetails, setPaymentProcessingDetails] = useState<
    PaymentProcessingDetails | undefined
  >();
  type PaymentState = "inactive" | "fetchingProcessingDetails" | "paying" | "paymentCleared";
  const [paymentState, setPaymentState] = useState<PaymentState>("inactive");
  const [showOrderDetails, setShowOrderDetails] = useState<boolean>(false);

  if (paymentState === "inactive" && isOpen && !!product) {
    setPaymentState("fetchingProcessingDetails");
  }

  // Initiates payment
  useEffect(() => {
    let isOutdated = false;

    const fetchPaymentUrl = async () => {
      try {
        if (paymentState !== "fetchingProcessingDetails") return;

        const payment = await new BackendClient().checkoutOne(product!.gtin);
        console.log(payment);

        if (!isOutdated) {
          setPaymentProcessingDetails(payment);
          setPaymentState("paying");
        }
      } catch (e) {
        console.error("Unexpected error", e);
      }
    };

    // noinspection JSIgnoredPromiseFromCall
    fetchPaymentUrl();

    return () => {
      isOutdated = true;
    };
  }, [paymentState, product]);

  const timeoutRef = useRef<NodeJS.Timeout>();

  // Polls the payment status
  useEffect(() => {
    const checkPaymentStatus = async () => {
      try {
        if (paymentState !== "paying") return;

        const status = await new BackendClient().getPaymentStatus(
          paymentProcessingDetails!.orderId
        );

        if (status === "cleared") {
          setPaymentState("paymentCleared");
        } else {
          timeoutRef.current = setTimeout(checkPaymentStatus, 1000);
        }
      } catch (e) {
        console.error("Unexpected error", e);
      }
    };

    // noinspection JSIgnoredPromiseFromCall
    checkPaymentStatus();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [paymentState, paymentProcessingDetails]);

  const onModalClosed = () => {
    setPaymentState("inactive");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} centered={true} size="md" toggle={onModalClosed} fade={true}>
      <ModalHeader toggle={onModalClosed}>{product?.name}</ModalHeader>
      <ModalBody className="p-0">
        {paymentState === "fetchingProcessingDetails" && (
          <div className="d-flex justify-content-center my-5">
            <Spinner color="primary" />
          </div>
        )}

        {paymentState === "paying" && (
          <iframe
            title="Checkout form"
            height="560"
            src={paymentProcessingDetails?.paymentFormUrl}
            frameBorder="0"
            allowFullScreen
          />
        )}

        {paymentState === "paymentCleared" && (
          <h4 className="my-5 text-success text-center">
            <i className="fa fa-check" /> Paid successfully!
          </h4>
        )}
      </ModalBody>
    </Modal>
  );
}

interface OrderDetailsModalProps {
  orderId?: string;
  isOpen: boolean;
  onClose: () => void;
}

function OrderDetailsModal({ orderId, isOpen, onClose }: OrderDetailsModalProps) {
  return (
    <Modal isOpen={isOpen} centered={true} size="md" toggle={onClose} fade={true}>
      <ModalHeader toggle={onClose} />
      <ModalBody className="p-0">{orderId && <OrderDetails orderId={orderId} />}</ModalBody>
    </Modal>
  );
}
