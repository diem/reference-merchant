import React from "react";
import { useTranslation } from "react-i18next";
import { PaymentEvent } from "../services/merchant";
import { Table } from "reactstrap";

export interface PaymentEventsProps {
  events: PaymentEvent[];
}

function PaymentEvents({ events }: PaymentEventsProps) {
  const { t } = useTranslation("order");
  return (
    <div className="d-flex justify-content-center">
      <Table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Event</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event, i) => (
            <tr key={i + 1}>
              <td>{event.timestamp.toLocaleString()}</td>
              <td>{t(`status.${event.eventType}`)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default PaymentEvents;
