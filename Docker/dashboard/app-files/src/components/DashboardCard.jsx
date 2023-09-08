import React from "react";
import "../style/card-style.css";
import CallMadeIcon from "@mui/icons-material/CallMade";
import SouthEastIcon from "@mui/icons-material/SouthEast";
export const DashboardCard = (props) => {
  return (
    <div className="card">
      <div className="title">{props.title}</div>
      <div className={"value " + props.valueColor}>{props.value}</div>
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
    </div>
  );
};
export default DashboardCard;
