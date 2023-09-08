import React, { useEffect, useState, PureComponent, useRef } from "react";
import ScaleIcon from "@mui/icons-material/Scale";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import Button from "@mui/material/Button";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
  Cell,
} from "recharts";

import "../style/data-page.css";
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import conf from "../conf.json";
import DashboardCard from "../components/DashboardCard";
import StatsCard from "../components/StatsCard";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import { over } from "stompjs";
import SocketJS from "sockjs-client";

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const colors = ["#ffc658", "#82ca9d"];

export const DataPage = () => {
  const [tempData, setTempData] = useState(null);
  const [loadData, setLoadData] = useState(null);
  const [fuelData, setFuelData] = useState(null);
  const tempDataRef = useRef([]);
  const loadDataRef = useRef([]);
  const fuelDataRef = useRef([]);
  const [stats, setStats] = useState(null);
  const [snackbar, setSnackbar] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const lastTempTime = useRef("");
  const lastFuelTime = useRef("");
  const lastLoadTime = useRef("");

  const navigate = useNavigate();

  const changeTempData = (data) => {
    if (data.length > 0) {
      const tempDataObj = handleTempData(data);
      setTempData(tempDataObj);
    }
  };
  const changeLoadData = (data) => {
    if (data.length > 0) {
      const loadDataObj = handleLoadData(data);
      setLoadData(loadDataObj);
    }
  };
  const changeFuelData = (data) => {
    if (data.length > 0) {
      const fuelDataObj = handleFuelData(data);
      setFuelData(fuelDataObj);
    }
  };
  const handleTempData = (data) => {
    const graphData = data.sort((a, b) => {
      return a.time.localeCompare(b.time);
    });
    const currentTemp = graphData[graphData.length - 1].value;
    const avgTemp =
      graphData.reduce((init, b) => {
        return init + b.value;
      }, 0) / graphData.length;
    const maxTemp = graphData
      .map((a) => a.value)
      .reduce((a, b) => {
        return Math.max(a, b);
      });
    const maxTime = graphData.filter((a) => {
      return a.value === maxTemp;
    })[0].time;
    const maxPerc = maxTemp / avgTemp;
    const currentPerc = currentTemp / avgTemp;
    const tempDataObj = {
      graphData,
      currentTemp,
      currentPerc,
      avgTemp,
      maxTemp,
      maxTime,
      maxPerc,
    };
    return tempDataObj;
  };
  const handleLoadData = (data) => {
    const graphData = data.sort((a, b) => {
      return a.time.localeCompare(b.time);
    });
    const currentLoad = graphData[graphData.length - 1].value;
    const avgLoad =
      graphData.reduce((init, b) => {
        return init + b.value;
      }, 0) / graphData.length;
    const sumLoad = graphData.reduce((init, b) => {
      return init + b.value;
    }, 0);
    const sumPerc = sumLoad / avgLoad;
    const currentPerc = currentLoad / avgLoad;
    const loadDataObj = {
      graphData,
      currentLoad,
      currentPerc,
      avgLoad,
      sumLoad,
      sumPerc,
    };
    return loadDataObj;
  };

  const handleFuelData = (data) => {
    const graphData = data.sort((a, b) => {
      return a.time.localeCompare(b.time);
    });
    const lastCriticalFuel = graphData[graphData.length - 1].value;
    const lastCriticalTime = graphData[graphData.length - 1].time;
    const minFuel = graphData
      .map((a) => a.value)
      .reduce((a, b) => {
        return Math.min(a, b);
      });
    const mins = graphData.filter((a) => {
      return a.value === minFuel;
    });
    let empty = 0;
    if (minFuel === 0) empty = mins.length;
    const minTime = mins[mins.length - 1].time;
    const fuelDataObj = {
      graphData,
      lastCriticalFuel,
      lastCriticalTime,
      minFuel,
      minTime,
      empty,
    };
    return fuelDataObj;
  };
  useEffect(() => {
    if (
      !sessionStorage.getItem("jwt") ||
      sessionStorage.getItem("jwt") === "" ||
      !sessionStorage.getItem("device") ||
      sessionStorage.getItem("device") === ""
    )
      navigate("/iot-platform/login");
    axios
      // .get(conf.server_url + `/data`, {
      .get(process.env.REACT_APP_API_URL + `/data`, {
        headers: {
          Authorization: "Bearer " + sessionStorage.getItem("jwt"),
        },
      })
      .then((res) => {
        // console.log(res.data);
        if (res.data.deviceStats.length > 0) {
          const collectedTempData = res.data.deviceStats.reduce((init, b) => {
            return init + b.tempDataBytes;
          }, 0);
          const usedTempData = res.data.deviceStats.reduce((init, b) => {
            return init + b.tempDataBytesForwarded;
          }, 0);
          const reductionTempPerc =
            collectedTempData !== 0 ? usedTempData / collectedTempData : 0;
          const collectedLoadData = res.data.deviceStats.reduce((init, b) => {
            return init + b.loadDataBytes;
          }, 0);
          const usedLoadData = res.data.deviceStats.reduce((init, b) => {
            return init + b.loadDataBytesForwarded;
          }, 0);
          const reductionLoadPerc =
            collectedLoadData !== 0 ? usedLoadData / collectedLoadData : 0;

          const collectedFuelData = res.data.deviceStats.reduce((init, b) => {
            return init + b.fuelDataBytes;
          }, 0);
          const usedFuelData = res.data.deviceStats.reduce((init, b) => {
            return init + b.fuelDataBytesForwarded;
          }, 0);
          const reductionFuelPerc = usedFuelData / collectedFuelData;
          setStats({
            collectedTempData: collectedTempData - usedTempData,
            usedTempData,
            reductionTempPerc,
            collectedLoadData: collectedLoadData - usedLoadData,
            usedLoadData,
            reductionLoadPerc,
            collectedFuelData: collectedFuelData - usedFuelData,
            usedFuelData,
            reductionFuelPerc,
          });
        }
        tempDataRef.current = res.data.temperatureData;
        loadDataRef.current = res.data.loadData;
        fuelDataRef.current = res.data.fuelData;
        changeFuelData(res.data.fuelData);
        changeTempData(res.data.temperatureData);
        changeLoadData(res.data.loadData);
        connect();
      })
      .catch((exc) => {
        let msg = "";
        if (exc.response.status === 401) msg = "Unauthorized access!";
        else msg = "Server unreachable!";
        setErrorMsg(msg);
        setSnackbar(true);
      });
  }, []);
  const logout = () => {
    navigate("/iot-dashboard/login");
  };
  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setSnackbar(false);
  };
  const onConnectionEstablished = (stompClient) => {
    //timeout after establishing connection required from unknown reasons
    setTimeout(() => {
      // subscribing user to topic that stores active users
      stompClient.subscribe(
        "/devices/" + sessionStorage.getItem("device") + "/load",
        (payload) => {
          const body = JSON.parse(payload.body);
          if (body.time !== lastLoadTime.current) {
            loadDataRef.current.push(body);
            console.log("-----------------LOAD---------------------");
            console.log(loadDataRef.current);
            console.log("------------------------------------------");
            changeLoadData(loadDataRef.current);
          }
          lastLoadTime.current = body.time;
        }
      );
      stompClient.subscribe(
        "/devices/" + sessionStorage.getItem("device") + "/fuel_level",
        (payload) => {
          const body = JSON.parse(payload.body);
          if (body.time !== lastFuelTime.current) {
            fuelDataRef.current.push(body);
            console.log("-----------------FUEL---------------------");
            console.log(fuelDataRef.current);
            console.log("------------------------------------------");
            changeFuelData(fuelDataRef.current);
          }
          lastFuelTime.current = body.time;
        }
      );
      stompClient.subscribe(
        "/devices/" + sessionStorage.getItem("device") + "/temperature",
        (payload) => {
          const body = JSON.parse(payload.body);
          if (body.time !== lastTempTime.current) {
            tempDataRef.current.push(body);
            console.log("-----------------TEMP---------------------");
            console.log(tempDataRef.current);
            console.log("------------------------------------------");
            changeTempData(tempDataRef.current);
          }
          lastTempTime.current = body.time;
        }
      );
    }, 100);
  };
  const onError = () => {
    setErrorMsg("Live data request failed!");
    setSnackbar(true);
  };
  const connect = () => {
    // const socket = new SocketJS(conf.server_url + "/ws");
    const socket = new SocketJS(process.env.REACT_APP_API_URL + "/ws");
    const stompClient = over(socket);
    stompClient.connect(
      {},
      () => onConnectionEstablished(stompClient),
      onError
    );
  };
  return (
    <div className="dashboard-page">
      <Snackbar
        open={snackbar}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity="error"
          sx={{ width: "100%" }}
        >
          {errorMsg}
        </Alert>
      </Snackbar>
      <Button
        variant="outlined"
        color="error"
        className="logout-btn"
        onClick={logout}
      >
        logout
      </Button>
      <div className="dashboard-container">
        <div className="cards-container">
          <div className="title-div">
            Engine temperature data
            <span>
              <DeviceThermostatIcon className="red-text"></DeviceThermostatIcon>
            </span>
          </div>
          <DashboardCard
            title="Current temperature"
            subtitle=""
            valueColor="blue-value"
            value={
              tempData != null
                ? tempData.currentTemp.toFixed(1) + "°C"
                : "Unknown"
            }
            second={
              tempData != null
                ? Math.round((tempData.currentPerc - 1) * 100)
                : "Unknown"
            }
            positive={false}
          />
          <DashboardCard
            title="Average temperature"
            subtitle="(last hour)"
            valueColor="green-value"
            value={
              tempData != null ? tempData.avgTemp.toFixed(1) + "°C" : "Unknown"
            }
            second=""
            positive={false}
          />
          <DashboardCard
            title="Max temperature"
            subtitle=""
            valueColor="red-value"
            value={
              tempData != null ? tempData.maxTemp.toFixed(1) + "°C" : "Unknown"
            }
            second={
              tempData != null
                ? Math.round((tempData.maxPerc - 1) * 100)
                : "Unknown"
            }
            positive={false}
          />
          <StatsCard
            title="Device temp stats"
            subtitle="Useful data"
            valueA={stats != null ? stats.collectedTempData : -1}
            valueB={stats != null ? stats.usedTempData : -1}
            second={stats != null ? stats.reductionTempPerc : -1}
          />
        </div>
        <div className="graph-area">
          {tempData && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                width={500}
                height={400}
                data={tempData.graphData}
                margin={{
                  top: 10,
                  right: 30,
                  left: 0,
                  bottom: 0,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  fill="#8884d8"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
      <div className="dashboard-container">
        <div className="cards-container">
          <div className="title-div">
            Excavator arm load data
            <span>
              <ScaleIcon className="red-text"></ScaleIcon>
            </span>
          </div>
          <DashboardCard
            title="Current load"
            subtitle=""
            valueColor="blue-value"
            value={
              loadData != null
                ? loadData.currentLoad.toFixed(1) + "kg"
                : "Unknown"
            }
            second={
              loadData != null
                ? Math.round((loadData.currentPerc - 1) * 100)
                : "Unknown"
            }
            positive={true}
          />
          <DashboardCard
            title="Average load"
            subtitle="(last hour)"
            valueColor="green-value"
            value={
              loadData != null ? loadData.avgLoad.toFixed(1) + "kg" : "Unknown"
            }
            second=""
            positive={false}
          />
          <DashboardCard
            title="Load sum"
            subtitle="(last hour)"
            valueColor="red-value"
            value={
              loadData != null ? loadData.sumLoad.toFixed(0) + "kg" : "Unknown"
            }
            second=""
            positive={true}
          />
          <StatsCard
            title="Device load stats"
            subtitle="Useful data"
            valueA={stats != null ? stats.collectedLoadData : -1}
            valueB={stats != null ? stats.usedLoadData : -1}
            second={stats != null ? stats.reductionLoadPerc : -1}
          />
        </div>
        <div className="graph-area">
          {loadData && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                width={500}
                height={400}
                data={loadData.graphData}
                margin={{
                  top: 10,
                  right: 30,
                  left: 0,
                  bottom: 0,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#ffc743"
                  fill="#ffc743"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
      <div className="dashboard-container">
        <div className="cards-container">
          <div className="title-div">
            Engine fuel level data
            <span>
              <LocalGasStationIcon className="red-text"></LocalGasStationIcon>
            </span>
          </div>
          <DashboardCard
            title="Last critical level"
            subtitle={fuelData ? fuelData.lastCriticalTime : "Unknown"}
            valueColor="blue-value"
            value={
              fuelData != null
                ? fuelData.lastCriticalFuel.toFixed(1) + "l"
                : "Unknown"
            }
            second=""
            positive={true}
          />
          <DashboardCard
            title="Empty fuel tank"
            value={fuelData ? "x" + fuelData.empty : "Unknown"}
            valueColor="green-value"
            subtitle={
              fuelData
                ? fuelData.empty > 0
                  ? "Be careful!"
                  : "Good job!"
                : "Unknown"
            }
            second=""
            positive={false}
          />
          <DashboardCard
            title="Min fuel level"
            subtitle={fuelData ? fuelData.minTime : "Unknown"}
            valueColor="red-value"
            value={
              fuelData != null ? fuelData.minFuel.toFixed(1) + "l" : "Unknown"
            }
            second=""
            positive={true}
          />
          <StatsCard
            title="Device fuel stats"
            subtitle="Useful data"
            valueA={stats != null ? stats.collectedFuelData : -1}
            valueB={stats != null ? stats.usedFuelData : -1}
            second={stats != null ? stats.reductionFuelPerc : -1}
          />
        </div>
        <div className="graph-area">
          {fuelData && (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                width={500}
                height={300}
                data={fuelData.graphData}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8">
                  {fuelData.graphData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={colors[index % colors.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};
export default DataPage;
