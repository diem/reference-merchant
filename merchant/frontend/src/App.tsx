import React from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";
import Header from "./components/Header";
import Home from "./pages/Home";
import "./i18n";
import "./assets/scss/diem-reference-merchant.scss";
import OrderDetailsPage from "./pages/OrderDetailsPage";
import ConfirmationPage from "./pages/ConfirmationPage";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main>
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/demo" render={(props) => <Home demoMode={true} {...props} />} />
          <Route path="/order/:orderId" component={ConfirmationPage} />
          <Route path="/admin/order/:orderId" component={OrderDetailsPage} />
          <Redirect to="/" />
        </Switch>
      </main>
    </BrowserRouter>
  );
}

export default App;
