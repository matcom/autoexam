module ApplicationHelper

  def buena_etiqueta(etiqueta)
    etiqueta.gsub(/[^a-zA-Z0-9]/, '-').gsub(/-+/,'-')
  end
end
