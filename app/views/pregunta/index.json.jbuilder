json.array!(@pregunta) do |preguntum|
  json.extract! preguntum, :titulo, :asignatura_id, :etiquetas
  json.url preguntum_url(preguntum, format: :json)
end
