import React, { useEffect, useState } from "react";
import "./PayWithDiem.css";
import {
  fetchAvailablePaymentOptions,
  PaymentOption,
} from "./blockchainService";
import {PaymentOptions} from "./vasp";

interface PayWithDiemProps {
  paymentInfo:PaymentOptions;
}

function PayWithDiem({ paymentInfo }: PayWithDiemProps) {
  const [paymentOptions, setPaymentOptions] = useState<PaymentOption[]>();
  const [link, setLink] = useState('')

  useEffect(() => {
    fetchAvailablePaymentOptions().then(setPaymentOptions);
  }, []);

  const vaspAddress = 'tdm1pgyne6my63v9j0ffwfnvn76mq398909f85gys03crzuwv0';
  const merchantName = 'acme-store';
  const checkoutDataType = 'PAYMENT_REQUEST';
  const action = 'CHARGE';
  const expiration = '2020-01-21T00%3A00%3A00.000Z';
  const redirectUrl = 'https://demo-merchant.diem.com/order/93c4963f-7f9e-4f9d-983e-7080ef782534/checkout/complete';

  useEffect(()=>{
    let redirect: string = '';
    if (paymentInfo !== undefined){
        redirect = `${paymentInfo.walletURL}/?vaspAddress=${vaspAddress}&referenceId=${paymentInfo.paymentId}&merchantName=${merchantName}&checkoutDataType=${checkoutDataType}&action=${action}&amount=${paymentInfo.options[0].amount}&currency=${paymentInfo.options[0].currency}&expiration=${expiration}&redirectUrl=${redirectUrl}`;
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
