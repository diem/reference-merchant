import React from "react";
import ReactDOM from "react-dom";
import * as serviceWorker from "./serviceWorker";
import PayWithPayPal from "./PayWithPayPal";
import PayWithCreditCard from "./PayWithCreditCard";
import "./index.css";
import LibraCheckout from "./components/LibraCheckout";

import "bootstrap/dist/css/bootstrap.min.css";

const query = new URLSearchParams(window.location.search);

ReactDOM.render(
  <React.StrictMode>
    <div className="payment-gateway">
      <h2 className="mb-4">Pay with Libra</h2>
      <LibraCheckout paymentId={query.get("payment")!} />
    </div>
    <div className="payment-gateway" style={{ opacity: 0.25 }}>
      <PayWithPayPal />
    </div>
    <div className="payment-gateway" style={{ opacity: 0.25 }}>
      <PayWithCreditCard />
    </div>
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
