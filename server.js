if (process.env.NODE_ENV !== "production") {
  require("dotenv").config();
}

// Imports
const express = require("express");
const app = express();
const expressLayouts = require("express-ejs-layouts");
const bodyParser = require("body-parser");
const methodOverride = require("method-override");
const bcrypt = require("bcrypt");
const passport = require("passport");
const LocalStrategy = require("passport-local").Strategy;
const flash = require("express-flash");
const session = require("express-session");
const MongoDBStore = require("connect-mongodb-session")(session);

// Models
const User = require("./models/user");
const Book = require("./models/book");

// Middleware
app.set("view engine", "ejs");
app.set("views", __dirname + "/views");
app.set("layout", "layouts/layout");
app.use(expressLayouts);
app.use(methodOverride("_method"));
app.use(express.static("public"));
app.use(express.urlencoded({ limit: "10mb", extended: false }));
app.use(express.json());
app.use(flash());
app.use(
  session({
    secret: process.env.SECRET_KEY,
    cookie: {
      maxAge: 1000 * 60 * 60 * 24 * 7, // 1 week
    },
    store: new MongoDBStore({
      uri: process.env.DATABASE_URL,
      collection: "sessions",
    }),
    resave: false,
    saveUninitialized: false,
  })
);

// Mongoose
// Make sure you start MongoDB locally (sudo systemctl start mongod)
const mongoose = require("mongoose");
mongoose
  .connect(process.env.DATABASE_URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .catch((err) => {
    console.error(Error, err.message);
  });

const db = mongoose.connection;
db.on("error", (error) => console.error(error));
db.on("open", () => console.log("Connected to Mongoose"));

// Passport
app.use(passport.initialize());
app.use(passport.session());

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => {
  User.findById(id, (err, user) => done(err, user));
});
passport.use(
  new LocalStrategy((username, password, done) => {
    User.findOne({ username: username }, (err, user) => {
      if (err) return done(err);
      if (!user) return done(null, false, { message: "Incorrect username" });

      bcrypt.compare(password, user.password, (err, res) => {
        if (err) return done(err);
        if (res === false)
          return done(null, false, { message: "Incorrect password" });

        return done(null, user);
      });
    });
  })
);

// Routers
app.use("/", require("./routes/index"));
app.use("/admin", require("./routes/admin"));
app.use("/authors", require("./routes/authors"));
app.use("/books", require("./routes/books"));
app.use("/series", require("./routes/series"));
app.use("/tags", require("./routes/tags"));

app.all("*", (req, res) => {
  res
    .status(404)
    .render("layouts/layout", { body: "<h2>404! Page not found</h2>" });
});

app.listen(process.env.PORT || 3000);
