import { ProductOrder } from "../services/merchant";
import { Table } from "reactstrap";
import React from "react";

interface OrderProductsProps {
  productOrders: ProductOrder[];
  total: number;
  currency: string;
}

function OrderProducts({ productOrders, total, currency }: OrderProductsProps) {
  return (
    <div className="d-flex justify-content-center">
      <Table>
        <thead>
          <tr>
            <th>#</th>
            <th>Product</th>
            <th className="text-right">Quantity</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {productOrders.map((productOrder, i) => (
            <tr key={i}>
              <th scope="row">{i + 1}</th>
              <td>{productOrder.product.name}</td>
              <td className="text-right">{productOrder.quantity}</td>
              <td>
                {productOrder.product.price / 1000000} {productOrder.product.currency}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th />
            <th />
            <th className="text-right">Total:</th>
            <th>
              {total / 1000000} {currency}
            </th>
          </tr>
        </tfoot>
      </Table>
    </div>
  );
}

export default OrderProducts;
