import React, { useEffect, useState } from "react";

import Vasp, { PaymentOptions } from "../vasp";
import {
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  Row,
  Col,
  Button,
} from "reactstrap";
import QRCode from "qrcode.react";
import PayWithLibra from "../PayWithLibra";
import { fiatToHumanFriendly, libraToHumanFriendly } from "../utils";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronLeft,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";

export interface LibraCheckoutProps {
  paymentId: string;
}

export default function LibraCheckout({ paymentId }: LibraCheckoutProps) {
  const [paymentOptions, setPaymentOptions] = useState<
    PaymentOptions | undefined
  >();
  const [selectedOption, setSelectedOption] = useState(0);
  const [chooseWallet, setChooseWallet] = useState(false);

  useEffect(() => {
    let isOutdated = false;

    const fetchOrder = async () => {
      try {
        const fetched = await new Vasp().getPaymentOptions(paymentId);

        if (!isOutdated) {
          setPaymentOptions(fetched);
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
  }, [paymentId]);

  const onCurrencyClick = (index: number) => setSelectedOption(index);

  if (!paymentOptions) {
    return <div>Loading...</div>;
  }
  return (
    <>
      <div className="w-100">
        <Row>
          <Col className="text-nowrap text-right">Total price:</Col>
          <Col className="text-nowrap">
            {fiatToHumanFriendly(paymentOptions.fiatPrice)}{" "}
            {paymentOptions.fiatCurrency}
          </Col>
        </Row>
        <Row>
          <Col className="text-nowrap text-right align-self-center">
            Payment currency:
          </Col>
          <Col>
            <UncontrolledDropdown>
              <DropdownToggle caret color="primary">
                {paymentOptions.options[selectedOption].currency}
              </DropdownToggle>
              <DropdownMenu>
                {paymentOptions.options.map((op, i) => (
                  <DropdownItem
                    key={op.currency}
                    onClick={() => onCurrencyClick(i)}
                  >
                    {op.currency}
                  </DropdownItem>
                ))}
              </DropdownMenu>
            </UncontrolledDropdown>
          </Col>
        </Row>
        <Row>
          <Col className="text-nowrap text-right">Total to pay:</Col>
          <Col className="text-nowrap">
            {libraToHumanFriendly(
              paymentOptions.options[selectedOption].amount
            )}{" "}
            {paymentOptions.options[selectedOption].currency}
          </Col>
        </Row>
      </div>
      <div>
        {chooseWallet ? (
          <>
            <Row>
              <Col className="py-4">
                <div className="text-center">Choose your wallet:</div>
                <PayWithLibra
                  paymentLink={
                    paymentOptions.options[selectedOption].paymentLink
                  }
                />
              </Col>
            </Row>
            <Row>
              <Col className="text-left">
                <Button onClick={() => setChooseWallet(false)}>
                  <FontAwesomeIcon icon={faChevronLeft} /> Scan QR
                </Button>
              </Col>
            </Row>
          </>
        ) : (
          <>
            <Row>
              <Col className="py-4">
                <QRCode
                  className="img-fluid"
                  size={256}
                  value={paymentOptions.options[selectedOption].paymentLink}
                  imageSettings={{
                    src: require("../logo.svg"),
                    height: 32,
                    width: 32,
                    excavate: true,
                  }}
                />
              </Col>
            </Row>
            <Row>
              <Col className="text-right">
                <Button onClick={() => setChooseWallet(true)}>
                  Open in Libra wallet <FontAwesomeIcon icon={faChevronRight} />
                </Button>
              </Col>
            </Row>
          </>
        )}
      </div>
    </>
  );
}
