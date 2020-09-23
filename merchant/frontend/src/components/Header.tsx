import React from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

const Header = () => {
  const { t } = useTranslation("layout");

  return (
    <>
      <header className="fixed-top d-inline-flex justify-content-between align-items-center">
        <div className="logo">
          <Link to="/">
            <img src={require("../assets/img/logo.svg")} alt={t("name")} />
          </Link>
        </div>
      </header>
      <div className="header-push" />
    </>
  );
};

export default Header;
