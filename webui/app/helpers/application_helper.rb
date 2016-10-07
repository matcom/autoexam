module ApplicationHelper

  def buena_etiqueta(etiqueta)
    etiqueta.gsub(/[^a-zA-Z0-9]/, '-').gsub(/-+/,'-')
  end

  def etiquetas_de(object)
    string = ''
    object.listado_de_etiquetas.each { |etiqueta| string += %<<span class="label">#{etiqueta}</span>  > }
    string.html_safe
  end
end
