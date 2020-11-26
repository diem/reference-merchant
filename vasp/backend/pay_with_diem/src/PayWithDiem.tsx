import React, { useEffect, useState } from "react";
import "./PayWithDiem.css";
import {
  fetchAvailablePaymentOptions,
  PaymentOption,
} from "./blockchainService";

interface PayWithDiemProps {
  paymentLink: string;
}

function PayWithDiem({ paymentLink }: PayWithDiemProps) {
  const [paymentOptions, setPaymentOptions] = useState<PaymentOption[]>();

  useEffect(() => {
    fetchAvailablePaymentOptions().then(setPaymentOptions);
  }, []);

  return (
    <div className="pay-with-diem">
      <div className="payment-options">
        {!paymentOptions && <span>Loading payment options...</span>}
        {paymentOptions && (
          <div className="">
            {paymentOptions.map((option) => (
              <div className="mt-4">
                <a
                  className="btn btn-block btn-primary text-left"
                  href={paymentLink}
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

export default PayWithDiem;
