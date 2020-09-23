import React, { useEffect, useState } from "react";
import "./PayWithLibra.css";
import {
  fetchAvailablePaymentOptions,
  PaymentOption,
} from "./blockchainService";

interface PayWithLibraProps {
  paymentLink: string;
}

function PayWithLibra({ paymentLink }: PayWithLibraProps) {
  const [paymentOptions, setPaymentOptions] = useState<PaymentOption[]>();

  useEffect(() => {
    fetchAvailablePaymentOptions().then(setPaymentOptions);
  }, []);

  return (
    <div className="pay-with-libra">
      <div className="payment-options">
        {!paymentOptions && <span>Loading payment options...</span>}
        {paymentOptions && (
          <div className="">
            {paymentOptions.map((option) => (
              <div className="my-4">
                <a
                  href={paymentLink}
                  className=""
                  key={option.id}
                >
                  <img
                    src={option.logo.base64}
                    alt={option.logo.alt}
                    height={32}
                  />{" "}
                  {option.name}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default PayWithLibra;
