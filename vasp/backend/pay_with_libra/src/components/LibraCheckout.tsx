import React, {useEffect, useState} from "react";

import Vasp, {PaymentOptions} from "../vasp";
import {
  Button,
  Col,
  DropdownItem,
  DropdownMenu,
  DropdownToggle,
  Row,
  UncontrolledDropdown,
  UncontrolledTooltip,
} from "reactstrap";
import QRCode from "qrcode.react";
import PayWithLibra from "../PayWithLibra";
import {fiatToHumanFriendly, libraToHumanFriendly} from "../utils";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faQuestionCircle,} from "@fortawesome/free-solid-svg-icons";

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
          <Col className="d-flex align-items-center">
            <span className="text-nowrap">
            {fiatToHumanFriendly(paymentOptions.fiatPrice)}{" "}
            {paymentOptions.fiatCurrency}
            </span>
            <FontAwesomeIcon size="xs" icon={faQuestionCircle} className="ml-2" id="totalPriceHelp" />
            <UncontrolledTooltip target="totalPriceHelp">
              The price in fiat set by the merchant
            </UncontrolledTooltip>
          </Col>
        </Row>
        <Row>
          <Col className="text-nowrap text-right align-self-center">
            Payment currency:
          </Col>
          <Col className="d-flex align-items-center">
            <UncontrolledDropdown>
              <DropdownToggle caret color="outline-dark" className="py-0 px-2">
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
            <FontAwesomeIcon size="xs" icon={faQuestionCircle} className="ml-2" id="currencyHelp" />
            <UncontrolledTooltip target="currencyHelp">
              Please select a Libra currency
            </UncontrolledTooltip>
          </Col>
        </Row>
        <Row>
          <Col className="text-nowrap text-right">Total to pay:</Col>
          <Col className="d-flex align-items-center">
            <span className="text-nowrap">
              {libraToHumanFriendly(
                paymentOptions.options[selectedOption].amount
              )}{" "}
              {paymentOptions.options[selectedOption].currency}
            </span>
            <FontAwesomeIcon size="xs" icon={faQuestionCircle} className="ml-2" id="totalToPayHelp" />
            <UncontrolledTooltip target="totalToPayHelp">
              The amount you will be changed in Libra
            </UncontrolledTooltip>
          </Col>
        </Row>
      </div>
      <div>
        {chooseWallet ? (
          <>
            <div className="mt-4">
              <div className="text-center">Choose your wallet:</div>
              <PayWithLibra
                paymentLink={
                  paymentOptions.options[selectedOption].paymentLink
                }
              />
            </div>
            <div className="text-center small py-4 font-weight-bold">
              - OR -
            </div>
            <div className="text-center">
              <Button color="primary" size="sm" onClick={() => setChooseWallet(false)}>
                Scan QR
              </Button>
            </div>
          </>
        ) : (
          <>
            <QRCode
              className="img-fluid mt-4"
              size={192}
              value={paymentOptions.options[selectedOption].paymentLink}
              imageSettings={{
                src: require("../logo.svg"),
                height: 32,
                width: 32,
                excavate: true,
              }}
            />
            <div className="text-center small py-4 font-weight-bold">
              - OR -
            </div>
            <div className="text-center">
              <Button color="primary" size="sm" onClick={() => setChooseWallet(true)}>
                Open in Libra wallet
              </Button>
              <FontAwesomeIcon size="xs" icon={faQuestionCircle} className="ml-2" id="openInWalletHelp" />
              <UncontrolledTooltip target="openInWalletHelp">
                Choose your Libra wallet
              </UncontrolledTooltip>
            </div>
          </>
        )}
      </div>
    </>
  );
}
