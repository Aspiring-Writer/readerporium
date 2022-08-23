const express = require("express");
const router = express.Router();
const passport = require("passport");
const bcrypt = require("bcrypt");

const { isLoggedIn, isLoggedOut } = require("../auth");
const User = require("../models/user");
const Book = require("../models/book");

router.get("/", isLoggedIn, async (req, res) => {
  let books;
  try {
    books = await Book.find({ accessLevel: { $lte: req.user.accessLevel }}).sort({ createAt: "desc" }).limit(10).exec();
  } catch {
    books = [];
  }
  res.render("index", { name: req.user.name, books: books });
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

router.get("/logout", isLoggedIn, (req, res, next) => {
  req.logout(function (err) {
    if (err) return next(err);
    res.redirect("/login");
  });
});

module.exports = router;
