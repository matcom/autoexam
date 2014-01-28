json.array!(@opcions) do |opcion|
  json.extract! opcion, :preguntum_id, :titulo, :right
  json.url opcion_url(opcion, format: :json)
end
