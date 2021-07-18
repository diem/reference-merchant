import React, { useEffect, useState } from "react";
import "./PayWithDiem.css";
import {
  fetchAvailablePaymentOptions,
  PaymentOption,
} from "./blockchainService";
import {PaymentOptions} from "./vasp";

interface PayWithDiemProps {
  paymentInfo:PaymentOptions;
  orderId: string;
  demoMode: boolean;
}

function PayWithDiem({ paymentInfo, orderId, demoMode }: PayWithDiemProps) {
  const [paymentOptions, setPaymentOptions] = useState<PaymentOption[]>();
  const [link, setLink] = useState('')

  useEffect(() => {
    fetchAvailablePaymentOptions().then(setPaymentOptions);
  }, []);
  
  const vaspAddress = paymentInfo.vaspAddress.split("'")[1];
  const merchantName = 'acme-store';
  const checkoutDataType = 'PAYMENT_REQUEST';
  const action = 'CHARGE';
  const expiration = encodeURIComponent(new Date(new Date().getTime() + 10 * 60000).toISOString());
  const redirectUrl = `${paymentInfo.baseMerchantURL}/order/${orderId}/checkout/complete`;
  const demo = demoMode ? '&demo=True' : "";

  useEffect(()=>{
    let redirect: string = '';
    if (paymentInfo !== undefined){
      redirect = `${paymentInfo.walletURL}/?vaspAddress=${vaspAddress}&referenceId=${orderId}`;

      if (demoMode){
        redirect = `${redirect}&merchantName=${merchantName}&checkoutDataType=${checkoutDataType}&action=${action}&amount=${paymentInfo.options[0].amount}&currency=${paymentInfo.options[0].currency}&expiration=${expiration}&redirectUrl=${redirectUrl}${demo}`;
      }
      setLink(redirect)
    }
  },[paymentInfo])

  const handleButtonClick = () => {
    window.parent.location.assign(link)
  }

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
                  onClick={handleButtonClick}
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
