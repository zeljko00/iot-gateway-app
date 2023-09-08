import React, { useEffect } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import OutlinedInput from "@mui/material/OutlinedInput";
import InputLabel from "@mui/material/InputLabel";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import FormControl from "@mui/material/FormControl";
import TextField from "@mui/material/TextField";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import "../style/login-page.css";
import excavator from "../assets/excavator-removebg-preview.png";
import Button from "@mui/material/Button";
import conf from "../conf.json";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import { useNavigate } from "react-router-dom";

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const LoginPage = () => {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [failed, setFailed] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const [snackbar, setSnackbar] = React.useState(false);
  const navigate = useNavigate();
  const handleClickShowPassword = () => setShowPassword((show) => !show);
  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };
  const usernameChanged = (event) => {
    let value = event.target.value;
    console.log(value);
    setUsername(value);
  };
  const passwordChanged = (event) => {
    let value = event.target.value;
    console.log(value);
    setPassword(value);
  };
  const submit = () => {
    const credentials = btoa(username + ":" + password);
    axios
      // .get(conf.server_url + `/auth/login`, {
      .get(process.env.REACT_APP_API_URL + `/auth/login`, {
        headers: {
          Authorization: "Basic " + credentials,
        },
      })
      .then((res) => {
        setFailed(false);
        const jwt = res.data;
        sessionStorage.setItem("jwt", jwt);
        sessionStorage.setItem("device", username);
        console.log(jwt);
        navigate("/iot-platform/dashboard");
      })
      .catch((exc) => {
        console.log(exc);
        if (exc.response.status === 401) setFailed(true);
        else setSnackbar(true);
      });
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setSnackbar(false);
  };

  return (
    <div className="login-page">
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
          Server can't be reached!
        </Alert>
      </Snackbar>
      <div className="logo-wrapper">
        <img src={excavator} alt="excavator"></img>
      </div>
      <div className="login-form-wrapper">
        <Box
          component="form"
          sx={{
            "& .MuiTextField-root": { m: 1, width: "25ch" },
          }}
          noValidate
          autoComplete="off"
        >
          <div>
            <TextField
              success
              id="outlined"
              label="Device username"
              onChange={usernameChanged}
              error={failed}
            />
            <br></br>
            <FormControl
              sx={{ m: 1, width: "25ch" }}
              variant="outlined"
              error={failed}
            >
              <InputLabel htmlFor="outlined-adornment-password">
                Device password
              </InputLabel>
              <OutlinedInput
                id="outlined-adornment-password"
                type={showPassword ? "text" : "password"}
                onChange={passwordChanged}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      onMouseDown={handleMouseDownPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                }
                label="Device password"
              />
            </FormControl>
            <br></br>
          </div>
        </Box>
        <div className="login-btn-wrapper">
          <Button variant="contained" onClick={submit}>
            Login
          </Button>
        </div>
      </div>
    </div>
  );
};
export default LoginPage;
