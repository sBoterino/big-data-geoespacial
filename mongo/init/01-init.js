// Inicialización de la base geoespacial. Solo corre al crear el volumen por primera vez.
// Crea las colecciones con un validador que rechaza GeoJSON mal formado y los índices 2dsphere.
const dbName = process.env.MONGO_DB || "geo";
const geo = db.getSiblingDB(dbName);

// Validador: location debe ser un Point GeoJSON con [longitud, latitud] en rango.
// Si alguien invierte el orden (lat, lon) con latitudes de NYC (~40) no lo detecta,
// por eso además existe una prueba automática con un punto conocido.
const validadorPunto = {
  $jsonSchema: {
    bsonType: "object",
    required: ["location"],
    properties: {
      location: {
        bsonType: "object",
        required: ["type", "coordinates"],
        properties: {
          type: { enum: ["Point"] },
          coordinates: {
            bsonType: "array",
            minItems: 2,
            maxItems: 2,
            items: [
              { bsonType: "number", minimum: -180, maximum: 180 },  // longitud
              { bsonType: "number", minimum: -90, maximum: 90 }     // latitud
            ]
          }
        }
      }
    }
  }
};

for (const nombre of ["eventos", "eventos_semilla"]) {
  if (!geo.getCollectionNames().includes(nombre)) {
    try {
      geo.createCollection(nombre, { validator: validadorPunto, validationLevel: "strict" });
    } catch (e) {
      // Si el validador no fuera aceptado, se sigue sin él: el índice 2dsphere igual rechaza
      // GeoJSON inválido. Así un error aquí no impide que MongoDB arranque.
      print(`[init] AVISO: validador no aplicado a ${nombre}: ${e.message}`);
      geo.createCollection(nombre);
    }
  }
  // La ingesta masiva puede eliminar y recrear este índice para cargar más rápido.
  geo[nombre].createIndex({ location: "2dsphere" }, { name: "location_2dsphere" });
  geo[nombre].createIndex({ fecha: 1 }, { name: "fecha_1" });
}

print(`[init] Base '${dbName}' lista: colecciones con validador GeoJSON e índices 2dsphere.`);
