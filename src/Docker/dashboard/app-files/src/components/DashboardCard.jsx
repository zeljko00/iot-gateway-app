import React from "react";
import "../style/card-style.css";
import CallMadeIcon from "@mui/icons-material/CallMade";
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import SouthEastIcon from "@mui/icons-material/SouthEast";
export const DashboardCard = (props) => {
  return (
    <div className={props.allert===true ? "alert-card": "card"}>
      <div className={props.allert ? "title red-value": "title"}>{props.title}</div>
      <div className={"value " + (props.allert ? "red-value": props.valueColor)}>{props.value}</div>
      <div
        className={
          "secondValue " +
          ((props.second > 0 && props.positive) ||
          (props.second < 0 && !props.positive)
            ? "green-value"
            : "red-value")
        }
      >
        {props.second ? (
          props.second > 0 ? (
            <CallMadeIcon></CallMadeIcon>
          ) : (
            <SouthEastIcon></SouthEastIcon>
          )
        ) : (
          ""
        )}
        {props.second !== "" ? props.second + "%" : ""}
      </div>
      <div className="subtitle">{props.subtitle}</div>
      {props.allert && <NotificationsActiveIcon className="alert-icon" color="error" sx={{ fontSize: 50}}></NotificationsActiveIcon>}
    </div>
  );
};
export default DashboardCard;
