import React from "react";
import ReactDOM from "react-dom";
import * as serviceWorker from "./serviceWorker";
import PayWithPayPal from "./PayWithPayPal";
import PayWithCreditCard from "./PayWithCreditCard";
import "./index.css";
import DiemCheckout from "./components/DiemCheckout";

import "bootstrap/dist/css/bootstrap.min.css";

const query = new URLSearchParams(window.location.search);

ReactDOM.render(
  <React.StrictMode>
    <div className="payment-gateway">
      <h2 className="mb-4">Pay with Diem</h2>
      <DiemCheckout paymentId={query.get("payment")!} orderId={query.get("orderId")}/>
    </div>
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
