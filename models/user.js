const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
  },
  username: {
    type: String,
    required: true,
  },
  password: {
    type: String,
    required: true,
  },
  dateCreated: {
    type: Date,
    required: true,
    default: Date.now,
  },
  role: {
    type: String,
    default: "member"
  },
  accessLevel: {
    type: Number,
    default: 1,
  },
});

module.exports = mongoose.model("User", userSchema);
