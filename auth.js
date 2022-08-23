function isLoggedIn(req, res, next) {
  if (req.isAuthenticated()) return next();
  res.redirect("/login");
}
function isLoggedOut(req, res, next) {
  if (!req.isAuthenticated()) return next();
  res.redirect("/");
}
const checkIsInRole =
  (...roles) =>
  (req, res, next) => {
    const hasRole = roles.find((role) => req.user.role === role);
    if (!hasRole) {
      return res.redirect("/");
    }
    return next();
  };

module.exports = { isLoggedIn, isLoggedOut, checkIsInRole };
