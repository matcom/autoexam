json.array!(@examen) do |examan|
  json.extract! examan, :nombre, :etiquetas, :directorio, :cantidad
  json.url examan_url(examan, format: :json)
end
