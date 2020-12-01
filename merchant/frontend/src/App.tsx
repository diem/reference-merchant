import React from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";
import Header from "./components/Header";
import Home from "./pages/Home";
import "./i18n";
// FIXME: DM
import "./assets/scss/libra-reference-merchant.scss";
import OrderDetails from "./pages/OrderDetails";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main>
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/admin/order/:orderId" component={OrderDetails} />
          <Redirect to="/" />
        </Switch>
      </main>
    </BrowserRouter>
  );
}

export default App;
