const express = require("express");
const router = express.Router();
const passport = require("passport");
const bcrypt = require("bcrypt");

const User = require("../models/user");
const Book = require("../models/book");

const { isLoggedIn, isLoggedOut, checkIsInRole } = require("../auth");
const ROLES = require("../roles");

router.get("/", isLoggedIn, async (req, res) => {
  let books;
  try {
    books = await Book.find().sort({ createAt: "desc" }).limit(10).exec();
  } catch {
    books = [];
  }
  res.render("index", { books: books });
});

router.get("/login", isLoggedOut, (req, res) => {
  res.render("login", { layout: false });
});

router.post(
  "/login",
  passport.authenticate("local", {
    successRedirect: "/",
    failureRedirect: "/login",
    failureFlash: true,
  })
);

router.get("/register", isLoggedIn, checkIsInRole(ROLES.ADMIN), (req, res) => {
  res.render("register");
});

router.post("/register", isLoggedIn, async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const newUser = new User({
      name: req.body.name,
      username: req.body.username,
      role: req.body.role,
      password: hashedPassword,
    });
    await newUser.save();
    res.redirect("/login");
  } catch {
    res.redirect("/register");
  }
});

router.get("/logout", isLoggedIn, (req, res, next) => {
  req.logout(function (err) {
    if (err) return next(err);
    res.redirect("/login");
  });
});
//isLoggedIn, checkIsInRole(ROLES.ADMIN),
router.get("/admin", async (req, res) => {
  try {
    const users = await User.find({});
    res.render("admin", { users: users });
  } catch {
    res.redirect("/");
  }
});

module.exports = router;
