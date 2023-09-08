import React, { PureComponent } from "react";
import { PieChart, Pie, Tooltip, Cell, ResponsiveContainer } from "recharts";
import "../style/card-style.css";
import CallMadeIcon from "@mui/icons-material/CallMade";
import SouthEastIcon from "@mui/icons-material/SouthEast";

const COLORS = ["#00C49F", "#FFBB28"];

export const StatsCard = (props) => {
  const data = [
    { name: "collected bytes", value: props.valueA },
    { name: "used bytes", value: props.valueB },
  ];
  return (
    <div className="card" id="stats-card">
      <div className="title">{props.title}</div>
      <div className="pie-area">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart width={400} height={400}>
            <Pie
              isAnimationActive={false}
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={78}
              fill="#8884d8"
              dataKey="value"
              label
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div
        className={
          "secondValue " + (props.second < 1 ? "green-value" : "red-value")
        }
      >
        {props.second !== "" ? (props.second * 100).toFixed(2) + "%" : ""}
      </div>
      <div className="subtitle">{props.subtitle}</div>
    </div>
  );
};
export default StatsCard;
