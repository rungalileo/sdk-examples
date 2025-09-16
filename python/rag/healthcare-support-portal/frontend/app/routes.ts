import { type RouteConfig, route, index, layout } from "@react-router/dev/routes";

export default [
  layout("routes/_layout.tsx", [
    index("routes/_index.tsx"),
    route("login", "routes/login.tsx"),
    route("demo-login", "routes/demo-login.tsx"),
    route("logout", "routes/logout.tsx"),
    route("patients", "routes/patients/index.tsx"),
    route("patients/new", "routes/patients/new.tsx"),
    route("patients/:id", "routes/patients/patient.tsx"),
    route("patients/:id/edit", "routes/patients/$id.edit.tsx"),
    route("chat", "routes/chat.tsx"),
    route("documents", "routes/documents.tsx"),
    route("documents/new", "routes/documents/new.tsx"),
    route("documents/:id", "routes/documents/$id.tsx"),
    route("users", "routes/users/index.tsx"),
    route("users/new", "routes/users/new.tsx"),
    route("users/:id/edit", "routes/users/$id.edit.tsx"),
    route("settings", "routes/settings.tsx"),
  ]),
] satisfies RouteConfig;