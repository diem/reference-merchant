import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardImg,
  CardText,
  CardTitle,
  Col,
  Container,
  Row,
} from "reactstrap";
import { Product } from "../interfaces/product";
import Payment from "../components/Payment";
import ProductsLoader from "../components/ProductsLoader";
import BackendClient from "../services/merchant";
import TestnetWarning from "../components/TestnetWarning";

function Home() {
  const { t } = useTranslation("layout");
  const [selectedProduct, setSelectedProduct] = useState<Product>();
  const [products, setProducts] = useState<Product[] | undefined>();

  const getProducts = async () => {
    try {
      setProducts(await new BackendClient().getProductsList());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    //noinspection JSIgnoredPromiseFromCall
    getProducts();
  }, []);

  return (
    <>
      <TestnetWarning />
      <Container>
        <h1 className="text-center font-weight-bold mt-5">{t("name")}</h1>

        <section className="mt-5">
          {products && (
            <Row>
              {products.map((product, i) => (
                <Col key={product.gtin} md={6} lg={4}>
                  <Card key={product.gtin} className="mb-4">
                    <CardImg
                      top
                      src="https://res.cloudinary.com/teepublic/image/private/s--7zJ6BFMp--/t_Resized%20Artwork/c_crop,x_10,y_10/c_fit,w_470/c_crop,g_north_west,h_626,w_470,x_0,y_0/g_north_west,u_upload:v1462829024:production:blanks:a59x1cgomgu5lprfjlmi,x_-395,y_-325/b_rgb:eeeeee/c_limit,f_jpg,h_630,q_90,w_630/v1544877956/production/designs/3743140_0.jpg"
                    />
                    <CardBody>
                      <CardTitle className="font-weight-bold h5">{product.name}</CardTitle>
                      <CardText>{product.description}</CardText>
                    </CardBody>
                    <CardFooter>
                      <Row>
                        <Col>
                          <div>
                            <strong>Price:</strong> {product.price / 1000000} {product.currency}
                          </div>
                          <div>
                            <strong>Payment Type:</strong>{" "}
                            <span className="text-capitalize">{product.payment_type}</span>
                          </div>
                        </Col>
                        <Col lg={4} className="text-right">
                          <Button
                            color="secondary"
                            block
                            className="btn-sm"
                            onClick={() => setSelectedProduct(products[i])}
                          >
                            Buy Now
                          </Button>
                        </Col>
                      </Row>
                    </CardFooter>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
          {!products && <ProductsLoader />}
        </section>
      </Container>
      <Payment
        product={selectedProduct}
        isOpen={!!selectedProduct}
        onClose={() => setSelectedProduct(undefined)}
      />
    </>
  );
}

export default Home;
