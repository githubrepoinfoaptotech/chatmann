module.exports = {
  name: "flask-app",
  script: "app.py",
  interpreter: "python3",
  watch: true,
  ignore_watch: ["node_modules", "venv"],
  env: {
    FLASK_ENV: "development",
    FLASK_APP: "app.py"
  }
};
