use std::{net::SocketAddr, path::{Path, PathBuf}};

use axum::{Router, routing::get, response::{Html, Redirect, Response, Json as JsonResponse}, http::{StatusCode, header, HeaderValue, response::Parts}, extract::Path as HttpPath};
use serde_json::Value as JsonValue;
use tower_http::services::ServeDir;

#[tokio::main]
async fn main() {
    // Inicializar tracing
    tracing_subscriber::fmt::init();

    // Rutas
    let app = Router::new()
        // Redirige / a /index.html
        .route("/", get(root))
        // Hace la carpeta / pública
        .route("/:fichero", get(obtener_html))
        // Hace la carpeta /geojson pública
        .route("/geojson/:fichero", get(obtener_geojson))
        // Hace la carpeta /css publica
        .nest_service("/css", ServeDir::new(Path::new("www").join("css")))
        // Hace la carpeta /js publica
        .nest_service("/js", ServeDir::new(Path::new("www").join("js")))
        // Hace la carpeta /svg publica
        .nest_service("/svg", ServeDir::new(Path::new("www").join("svg")));

    // Iniciar servidor (en la ip: 127.0.0.1:3000)
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    tracing::info!("listening on http://{}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn root() -> Redirect {
    Redirect::permanent("/index.html")
}

fn obtener_fichero(ruta: PathBuf) -> Result<String, StatusCode> {
    let ruta = Path::new("www")
        .join(ruta);
    tracing::info!("{ruta:?}");
    std::fs::read_to_string(ruta).map_err(|_| StatusCode::NOT_FOUND)
}

async fn obtener_html(HttpPath(fichero): HttpPath<String>) -> Result<Html<String>, StatusCode> {
    Ok(Html(obtener_fichero(
        Path::new(&fichero).into()
    )?))
}

async fn obtener_geojson(HttpPath(fichero): HttpPath<String>) -> Result<JsonResponse<JsonValue>, StatusCode> {
    let cuerpo = obtener_fichero(
        Path::new("geojson")
        .join(&fichero)
    )?;
    let cuerpo = serde_json::from_str(&cuerpo).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(JsonResponse(cuerpo))
}
