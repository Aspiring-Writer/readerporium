if (process.env.NODE_ENV !== "production") {
  require("dotenv").config();
}

const express = require("express");
const app = express();
const expressLayouts = require("express-ejs-layouts");
const bodyParser = require("body-parser");

const indexRouter = require("./routes/index");
const authorRouter = require("./routes/authors");

app.set("view engine", "ejs");
app.set("views", __dirname + "/views");
app.set("layout", "layouts/layout");
app.use(expressLayouts);
app.use(express.static("public"));
app.use(express.urlencoded({ limit: "10mb", extended: false }));
app.use(express.json())

// Make sure you start MongoDB locally (sudo systemctl start mongod)
const mongoose = require("mongoose");
mongoose
  .connect(process.env.DATABASE_URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .catch((err) => {
    console.log(Error, err.message);
  });

const db = mongoose.connection;
db.on("error", (error) => console.error(error));
db.on("open", () => console.log("Connected to Mongoose"));

app.use("/", indexRouter);
app.use("/authors", authorRouter);

app.listen(process.env.PORT || 3000);
