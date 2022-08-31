const express = require("express");
const router = express.Router();
const passport = require("passport");
const bcrypt = require("bcrypt");
const { isLoggedIn, isAdmin } = require("../auth");
const User = require("../models/user");
const Book = require("../models/book");

// Admin Route
router.get("/", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const users = await User.find({});
    res.render("admin", { users: users });
  } catch {
    res.redirect("/admin");
  }
});

// New User
router.get("/new", isLoggedIn, isAdmin, (req, res) => {
  res.render("new");
});

// Create User
router.post("/", async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const newUser = new User({
      name: req.body.name,
      username: req.body.username,
      accessLevel: req.body.accessLevel,
      role: req.body.role,
      password: hashedPassword,
    });
    await newUser.save();
    res.redirect("/admin");
  } catch {
    res.redirect("/admin");
  }
});

// Edit User Route
router.get("/:id/edit", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    res.render("edit", { ROLES: ROLES, user: user });
  } catch {
    res.redirect("/admin");
  }
});

// Update User Route
router.put("/:id", async (req, res) => {
  let user;
  try {
    user = await User.findById(req.params.id);
    user.name = req.body.name;
    user.username = req.body.username;
    user.accessLevel = req.body.accessLevel;
    user.role = req.body.role;
    await user.save();
    res.redirect("/admin");
  } catch {
    if (user == null) {
      res.redirect("/admin");
    } else {
      req.flash("error", "Error updating user");
      res.render("edit", {
        user: user,
      });
    }
  }
});

// Delete User
router.delete("/:id", isLoggedIn, isAdmin, async (req, res) => {
  let user;
  try {
    user = await User.findById(req.params.id);
    await user.remove();
    res.redirect("/admin");
  } catch {
    if (user == null) {
      res.redirect("/admin");
    } else {
      res.send("Error removing user");
    }
  }
});

module.exports = router;
