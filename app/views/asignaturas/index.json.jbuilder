json.array!(@asignaturas) do |asignatura|
  json.extract! asignatura, :nombre_corto, :nombre_largo, :descripcion
  json.url asignatura_url(asignatura, format: :json)
end
