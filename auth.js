function isLoggedIn(req, res, next) {
  if (req.isAuthenticated()) return next();
  res.redirect("/login");
}
function isLoggedOut(req, res, next) {
  if (!req.isAuthenticated()) return next();
  res.redirect("/");
}
function isAdmin(req, res, next) {
  if (req.user.role == "admin") return next();
  res.status(403).render("layouts/layout", { body: "<h2>403! Forbidden</h2>" });
}

module.exports = { isLoggedIn, isLoggedOut, isAdmin };
