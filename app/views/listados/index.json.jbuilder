json.array!(@listados) do |listado|
  json.extract! listado, :asignatura_id, :estudiantes
  json.url listado_url(listado, format: :json)
end
